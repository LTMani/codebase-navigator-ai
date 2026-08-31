import time
from collections import defaultdict
from typing import Dict, List
from flask import request
from app.errors.exceptions import RateLimitError


class InMemoryRateLimiter:
    """Sliding window in-memory rate limiter per IP address."""

    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.request_history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Filter timestamps outside sliding window
        self.request_history[client_ip] = [ts for ts in self.request_history[client_ip] if ts > cutoff]
        
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            return False

        self.request_history[client_ip].append(now)
        return True


limiter = InMemoryRateLimiter(requests_per_minute=200)


def check_rate_limit():
    """Hook to evaluate incoming client request against rate limits."""
    client_ip = request.remote_addr or "127.0.0.1"
    if not limiter.is_allowed(client_ip):
        raise RateLimitError("Rate limit exceeded. Maximum 200 requests per minute allowed.")
