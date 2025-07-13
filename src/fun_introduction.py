from functools import wraps
from src.logging import logger

def introduce(func):
    """Decorator that emits a visual delimiter and the caller’s name **before**
    the wrapped method executes.

    The log entry makes it easy to spot high-level transitions in the
    application’s output when debugging.

    Args:
        func (Callable): The instance method being wrapped.

    Returns:
        Callable: The wrapped method, unchanged in signature.
    """
    @wraps(func)
    def introduce_before_call(*args, **kwargs):
        # args[0] is always the instance (`self`) for bound methods
        logger.info("\n%s\n%s:", "*-" * 37, args[0])
        return func(*args, **kwargs)

    return introduce_before_call