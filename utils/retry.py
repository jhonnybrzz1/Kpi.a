import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: int = 1):
    """Decorator to retry function calls with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error("Failed after %d attempts: %s", max_retries, str(e))
                        raise
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        "Attempt %d failed, retrying in %ds: %s", attempt + 1, delay, str(e)
                    )
                    time.sleep(delay)

        return wrapper

    return decorator
