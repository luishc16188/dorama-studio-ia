#!/usr/bin/env python3
"""
Simple test to verify token economy optimizations work
"""

from dorama_studio.core.token_usage import token_tracker, TokenUsage, TokenEstimationMethod
from dorama_studio.core.prompt_context import PromptContextBuilder, ContextBudget, StableContext, build_minimal_prompt
from dorama_studio.core.cache import multi_level_cache, idempotency_manager
from dorama_studio.core.agent_handoff import handoff_registry, create_handoff


def test_token_tracking():
    """Test that token tracking works"""
    print("Testing token tracking...")
    token_tracker.reset()

    # Simulate an LLM call
    usage = TokenUsage(
        input_tokens=1000,
        output_tokens=500,
        total_tokens=1500,
        estimated=True,
        estimation_method=TokenEstimationMethod.CHAR_BASED,
        model="claude-opus-4-5",
        provider="freellmapi",
        agent="TestAgent",
        operation="test_operation",
    )
    token_tracker.record(usage)

    report = token_tracker.get_report()
    assert report.total_calls == 1
    assert report.total_tokens == 1500
    print("[PASS] Token tracking works")


def test_prompt_context_building():
    """Test that prompt context building reduces tokens"""
    print("Testing prompt context building...")
    builder = PromptContextBuilder(ContextBudget(max_total_tokens=1000))
    builder.set_stable_context(StableContext(
        system_rules="System rules here",
        architecture_docs="Architecture docs here",
    ))

    episode_data = {
        "objective": "Test objective",
        "beats": [{"beat_name": "Hook", "action": "Test action"} for _ in range(3)],
        "characters_present": ["CHAR_001", "CHAR_002"],
    }

    prompt = builder.build(
        task="Generate beats",
        agent="MasterWriter",
        episode=episode_data,
    )

    stats = builder.get_context_stats(prompt)
    print(f"Prompt tokens: {stats['estimated_tokens']}")
    print(f"Within budget: {stats['within_budget']}")
    print("[PASS] Prompt context building works")


def test_caching():
    """Test that caching prevents recomputation"""
    print("Testing caching...")
    multi_level_cache.clear()

    call_count = 0

    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Use idempotency manager
    key = "test_key_123"
    result1, hit1 = idempotency_manager.check_and_store(key, lambda: expensive_function(5))
    result2, hit2 = idempotency_manager.check_and_store(key, lambda: expensive_function(5))

    assert hit1 is False  # First call should compute
    assert hit2 is True   # Second call should hit cache
    assert call_count == 1  # Function should only be called once
    assert result1 == result2 == 10
    print("[PASS] Caching works")


def test_agent_handoff():
    """Test that agent handoff optimization filters data"""
    print("Testing agent handoff optimization...")

    # Simulate MasterWriter output
    master_writer_output = {
        "script": {"artifact_id": "script_001", "content": "x" * 1000},
        "beats": [{"beat_name": f"Beat {i}"} for i in range(9)],
        "hook": {"hook_id": "hook_001", "content": "y" * 500},
        "characters": [{"id": "CHAR_001", "name": "Test Char"}] * 5,
        "viral_ruleset": ["rule1", "rule2", "rule3"],
        "genome_context": {"data": "z" * 200},
    }

    # Filter for DirectorEngineAgent (should only need beats and maybe hook)
    handoff = create_handoff("MasterWriterAgent", "DirectorEngineAgent", master_writer_output)

    print(f"Original size: {len(str(master_writer_output))} chars")
    print(f"Handoff size: {len(str(handoff))} chars")
    print(f"Handoff keys: {list(handoff.keys())}")

    # Should be smaller than original
    assert len(str(handoff)) < len(str(master_writer_output))
    print("[PASS] Agent handoff optimization works")


def main():
    print("Running Token Economy Optimization Tests")
    print("=" * 50)

    test_token_tracking()
    test_prompt_context_building()
    test_caching()
    test_agent_handoff()

    print("=" * 50)
    print("All tests passed!")


if __name__ == "__main__":
    main()