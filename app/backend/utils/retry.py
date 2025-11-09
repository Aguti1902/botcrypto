"""Retry utilities with exponential backoff."""
import time
from functools import wraps
from typing import Callable, Type, TypeVar
from loguru import logger
import asyncio

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """Decorator for retrying a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback called on each retry with (exception, attempt)
    """
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}",
                            extra={"error": str(e), "attempts": attempt},
                        )
                        raise
                    
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay:.2f}s",
                        extra={"error": str(e), "delay": delay},
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(delay)
            
            raise RuntimeError(f"Should not reach here: {func.__name__}")
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}",
                            extra={"error": str(e), "attempts": attempt},
                        )
                        raise
                    
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay:.2f}s",
                        extra={"error": str(e), "delay": delay},
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(delay)
            
            raise RuntimeError(f"Should not reach here: {func.__name__}")
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

