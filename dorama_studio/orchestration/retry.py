"""
Retry policies for DORAMA STUDIO orchestration.
Provides configurable retry logic with exponential backoff.
"""

import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy(Enum):
    """Retry strategy types."""
    FIXED = "fixed"           # Fixed delay
    EXPONENTIAL = "exponential"  # Exponential backoff
    LINEAR = "linear"         # Linear increase
    FIBONACCI = "fibonacci"   # Fibonacci sequence


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0          # Base delay in seconds
    max_delay: float = 60.0          # Maximum delay cap
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True              # Add random jitter
    jitter_factor: float = 0.1       # Jitter as fraction of delay

    # Retryable exceptions (None = all exceptions)
    retryable_exceptions: tuple[type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        IOError,
    )

    # Non-retryable exceptions (always raised immediately)
    non_retryable_exceptions: tuple[type[Exception], ...] = (
        ValueError,
        TypeError,
        KeyError,
    )

    # Callback on retry
    on_retry: Callable[[int, Exception, float], None] | None = None

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (2 ** attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        elif self.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci: 1, 1, 2, 3, 5, 8, 13...
            a, b = 1, 1
            for _ in range(attempt):
                a, b = b, a + b
            delay = self.base_delay * a
        else:
            delay = self.base_delay

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter
        if self.jitter:
            jitter_range = delay * self.jitter_factor
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    def is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable."""
        # Check non-retryable first (higher priority)
        if isinstance(exception, self.non_retryable_exceptions):
            return False
        # Check retryable
        return isinstance(exception, self.retryable_exceptions)


class RetryPolicy:
    """
    Retry policy executor with configurable behavior.

    Usage:
        policy = RetryPolicy(RetryConfig(max_attempts=5, base_delay=2.0))
        result = policy.execute(my_function, arg1, arg2)

        # Or as decorator:
        @policy.decorate
        def my_function(...):
            ...
    """

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()

    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with retry policy.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted
        """
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self.config.is_retryable(e) or attempt == self.config.max_attempts - 1:
                    logger.error(
                        f"Retry policy: non-retryable or max attempts reached. "
                        f"Attempt {attempt + 1}/{self.config.max_attempts}. Error: {e}"
                    )
                    raise

                # Calculate delay
                delay = self.config.calculate_delay(attempt)

                logger.warning(
                    f"Retry policy: attempt {attempt + 1}/{self.config.max_attempts} failed. "
                    f"Retrying in {delay:.2f}s. Error: {e}"
                )

                # Callback
                if self.config.on_retry:
                    try:
                        self.config.on_retry(attempt + 1, e, delay)
                    except Exception as cb_e:
                        logger.error(f"Retry callback error: {cb_e}")

                # Sleep
                time.sleep(delay)

        # Should not reach here, but just in case
        raise last_exception

    def decorate(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to apply retry policy to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper

    @classmethod
    def with_config(cls, **kwargs) -> 'RetryPolicy':
        """Create policy with inline config."""
        return cls(RetryConfig(**kwargs))


# ============================================================
# Specialized Retry Policies
# ============================================================

# Quick retry for transient failures
QUICK_RETRY = RetryPolicy(RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=5.0,
    strategy=RetryStrategy.EXPONENTIAL,
))

# Standard retry for API calls
STANDARD_RETRY = RetryPolicy(RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
))

# Aggressive retry for critical operations
AGGRESSIVE_RETRY = RetryPolicy(RetryConfig(
    max_attempts=10,
    base_delay=2.0,
    max_delay=120.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
))

# Fibonacci retry for rate-limited APIs
FIBONACCI_RETRY = RetryPolicy(RetryConfig(
    max_attempts=8,
    base_delay=1.0,
    max_delay=60.0,
    strategy=RetryStrategy.FIBONACCI,
    jitter=True,
))

# No retry policy
NO_RETRY = RetryPolicy(RetryConfig(
    max_attempts=1,
))


# ============================================================
# Async Retry Support
# ============================================================

async def async_execute_with_retry(
    func: Callable[..., Any],
    *args,
    config: RetryConfig | None = None,
    **kwargs
) -> Any:
    """Execute async function with retry policy."""
    config = config or RetryConfig()
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if not config.is_retryable(e) or attempt == config.max_attempts - 1:
                logger.error(f"Async retry exhausted: {e}")
                raise

            delay = config.calculate_delay(attempt)

            logger.warning(f"Async retry {attempt + 1}/{config.max_attempts} in {delay:.2f}s: {e}")

            if config.on_retry:
                try:
                    config.on_retry(attempt + 1, e, delay)
                except Exception:
                    pass

            import asyncio
            await asyncio.sleep(delay)

    raise last_exception


def async_retry(config: RetryConfig | None = None):
    """Async retry decorator."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await async_execute_with_retry(func, *args, config=config, **kwargs)
        return wrapper
    return decorator
