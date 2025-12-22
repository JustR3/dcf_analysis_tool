"""Shared utilities for the quant-portfolio-manager."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


class RateLimiter:
    """Rate limiter for API calls (~60 calls/minute recommended for yfinance)."""

    def __init__(self, calls_per_minute: int = 60):
        self.min_interval = 60 / calls_per_minute
        self.last_call = 0.0

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper

    def wait(self) -> None:
        """Manual rate limit wait."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


# Global shared rate limiter instance
rate_limiter = RateLimiter(calls_per_minute=60)
