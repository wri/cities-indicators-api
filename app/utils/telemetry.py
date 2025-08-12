import logging
import time
import functools
import inspect
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def _log_duration(logger: logging.Logger, qualname: str, duration_ms: float) -> None:
    logger.debug("TIMER %s took %.2f ms", qualname, duration_ms)


def timed(func: F) -> F:
    """Decorator to log execution duration of a function at DEBUG level.

    Works for both sync and async functions. Keeps original signature and name.
    """

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)
            start = time.perf_counter()
            try:
                return await cast(Callable[..., Any], func)(*args, **kwargs)
            finally:
                _log_duration(logger, func.__qualname__, (time.perf_counter() - start) * 1000)

        return cast(F, async_wrapper)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(func.__module__)
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            _log_duration(logger, func.__qualname__, (time.perf_counter() - start) * 1000)

    return cast(F, sync_wrapper)


def set_root_log_level(level: int) -> None:
    """Set root logger level safely (keeps existing handlers)."""
    logging.getLogger().setLevel(level)
