import logging
import os
import time
from typing import Any

from pydantic import BaseModel

from dorama_studio.core.cache import (
    CacheEntry,
    idempotency_manager,
    multi_level_cache,
)

# Import token tracking and caching
from dorama_studio.core.token_usage import TokenEstimationMethod, token_tracker

logger = logging.getLogger(__name__)

# Try to import freellmapi client
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def call_llm(
    prompt: str,
    model: str = "freellmapi/claude-opus-4-5",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = None,
) -> str:
    """
    Call LLM with simple text completion.

    Args:
        prompt: User prompt
        model: Model identifier (e.g., freellmapi/claude-opus-4-5)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt

    Returns:
        Generated text response
    """
    provider, model_name = _parse_model(model)

    if provider == "freellmapi" or provider == "openai":
        return _call_openai_compatible(
            prompt, model_name, temperature, max_tokens, system_prompt
        )
    elif provider == "anthropic":
        return _call_anthropic(
            prompt, model_name, temperature, max_tokens, system_prompt
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def call_llm_structured(
    prompt: str,
    schema: type[BaseModel],
    model: str = "freellmapi/claude-opus-4-5",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    system_prompt: str = None,
) -> BaseModel:
    """
    Call LLM with structured output using Pydantic schema.

    Args:
        prompt: User prompt
        schema: Pydantic model class for output validation
        model: Model identifier
        temperature: Sampling temperature (low for structured output)
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt

    Returns:
        Validated Pydantic model instance
    """
    provider, model_name = _parse_model(model)

    # Add schema instructions to prompt
    schema_json = schema.model_json_schema()
    structured_prompt = f"{prompt}\n\nOUTPUT MUST BE VALID JSON MATCHING THIS SCHEMA:\n{json.dumps(schema_json, ensure_ascii=False)}"

    response_text = call_llm(
        structured_prompt, model_name, temperature, max_tokens, system_prompt
    )

    try:
        # Extract JSON from response (handle markdown code blocks)
        json_text = _extract_json(response_text)
        data = json.loads(json_text)
        return schema(**data)
    except Exception as e:
        logger.error(f"Failed to parse structured output: {e}")
        logger.error(f"Raw response: {response_text[:500]}")
        raise


def _parse_model(model: str) -> tuple[str, str]:
    """Parse model string into provider and model name."""
    if "/" in model:
        provider, model_name = model.split("/", 1)
    else:
        provider = "freellmapi"
        model_name = model
    return provider, model_name


def _call_openai_compatible(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str = None,
) -> str:
    """Call OpenAI-compatible API (freellmapi, local servers)."""
    if not OPENAI_AVAILABLE:
        raise RuntimeError(
            "openai package not installed. Install with: pip install openai"
        )

    client = openai.OpenAI(
        base_url=os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:31415/v1"),
        api_key=os.getenv("FREELLMAPI_API_KEY", "dummy-key"),
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
    )

    return response.choices[0].message.content


def _call_anthropic(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str = None,
) -> str:
    """Call Anthropic API directly."""
    if not ANTHROPIC_AVAILABLE:
        raise RuntimeError(
            "anthropic package not installed. Install with: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    messages = [{"role": "user", "content": prompt}]

    response = client.messages.create(
        model=model,
        messages=messages,
        system=system_prompt or "",
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.content[0].text


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Remove markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        return text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        return text[start:end].strip()
    return text.strip()


# ============================================================
# Enhanced LLM calls with token tracking, caching, idempotency
# ============================================================

def call_llm_tracked(
    prompt: str,
    model: str = "freellmapi/claude-opus-4-5",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = None,
    agent: str = "unknown",
    operation: str = "llm_call",
    episode_id: str = None,
    season_id: str = None,
    project_id: str = None,
    scene_id: str = None,
    stable_context: Any = None,
    dynamic_context: Any = None,
    task_input: Any = None,
    prompt_version: str = "1.0",
    use_cache: bool = True,
    cache_ttl: float = 86400,
) -> str:
    """
    Call LLM with full token tracking, caching, and idempotency.

    Args:
        prompt: User prompt (or full prompt including system)
        model: Model identifier
        temperature: Sampling temperature
        max_tokens: Max output tokens
        system_prompt: System prompt
        agent: Agent name for tracking
        operation: Operation name for tracking
        episode_id: Episode ID for tracking
        season_id: Season ID for tracking
        project_id: Project ID for tracking
        scene_id: Scene ID for tracking
        stable_context: Stable context for cache key
        dynamic_context: Dynamic context for cache key
        task_input: Task input for cache key
        prompt_version: Prompt version for cache invalidation
        use_cache: Whether to use idempotency cache
        cache_ttl: Cache TTL in seconds

    Returns:
        Generated text response
    """
    provider, model_name = _parse_model(model)

    # Build full prompt for tracking
    full_prompt = ""
    if system_prompt:
        full_prompt += f"SYSTEM: {system_prompt}\n\n"
    full_prompt += prompt

    # Generate cache key if contexts provided
    cache_key = None
    if use_cache and stable_context is not None and dynamic_context is not None and task_input is not None:
        cache_key = idempotency_manager.generate_key(
            agent=agent,
            operation=operation,
            stable_context=stable_context,
            dynamic_context=dynamic_context,
            task_input=task_input,
            model=model_name,
            provider=provider,
            prompt_version=prompt_version,
        )

    # Check cache first
    if cache_key:
        cached_entry = multi_level_cache.get(cache_key)
        if cached_entry and not cached_entry.is_expired(cache_ttl):
            logger.info(f"Cache HIT for {agent}.{operation} (key: {cache_key[:32]})")
            # Track cache hit
            token_tracker.record_token_usage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                estimated=True,
                estimation_method=TokenEstimationMethod.CHAR_BASED,
                model=model_name,
                provider=provider,
                agent=agent,
                operation=operation,
                cache_hit=True,
                latency_ms=0,
                episode_id=episode_id,
                season_id=season_id,
                project_id=project_id,
                scene_id=scene_id,
            )
            return cached_entry.value

    # Execute LLM call with tracking
    start_time = time.time()

    with token_tracker.track_call(
        agent=agent,
        operation=operation,
        model=model_name,
        provider=provider,
        episode_id=episode_id,
        season_id=season_id,
        project_id=project_id,
        scene_id=scene_id,
    ) as ctx:
        if provider == "freellmapi" or provider == "openai":
            response = _call_openai_compatible(
                prompt, model_name, temperature, max_tokens, system_prompt
            )
        elif provider == "anthropic":
            response = _call_anthropic(
                prompt, model_name, temperature, max_tokens, system_prompt
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        latency_ms = int((time.time() - start_time) * 1000)
        ctx.set_result(
            input_text=full_prompt,
            output_text=response,
            estimated=True,
            estimation_method=TokenEstimationMethod.CHAR_BASED,
            cache_hit=False,
        )

    # Store in cache
    if cache_key:
        entry = CacheEntry(
            key=cache_key,
            value=response,
            dependencies=[],
            metadata={"model": model_name, "provider": provider, "temperature": temperature},
        )
        multi_level_cache.set(cache_key, entry)
        logger.info(f"Cached response for {agent}.{operation} (key: {cache_key[:32]})")

    return response


def call_llm_structured_tracked(
    prompt: str,
    schema: type[BaseModel],
    model: str = "freellmapi/claude-opus-4-5",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    system_prompt: str = None,
    agent: str = "unknown",
    operation: str = "llm_structured",
    episode_id: str = None,
    season_id: str = None,
    project_id: str = None,
    scene_id: str = None,
    stable_context: Any = None,
    dynamic_context: Any = None,
    task_input: Any = None,
    prompt_version: str = "1.0",
    use_cache: bool = True,
    cache_ttl: float = 86400,
) -> BaseModel:
    """
    Call LLM with structured output and full tracking.
    """
    provider, model_name = _parse_model(model)

    # Add schema to prompt
    schema_json = schema.model_json_schema()
    structured_prompt = f"{prompt}\n\nOUTPUT MUST BE VALID JSON MATCHING THIS SCHEMA:\n{json.dumps(schema_json, ensure_ascii=False)}"

    # Use tracked call
    response_text = call_llm_tracked(
        prompt=structured_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        agent=agent,
        operation=operation,
        episode_id=episode_id,
        season_id=season_id,
        project_id=project_id,
        scene_id=scene_id,
        stable_context=stable_context,
        dynamic_context=dynamic_context,
        task_input=task_input,
        prompt_version=prompt_version,
        use_cache=use_cache,
        cache_ttl=cache_ttl,
    )

    try:
        json_text = _extract_json(response_text)
        data = json.loads(json_text)
        return schema(**data)
    except Exception as e:
        logger.error(f"Failed to parse structured output: {e}")
        logger.error(f"Raw response: {response_text[:500]}")
        raise


# Import CacheEntry for type hint
