import asyncio
import time
from collections import deque


class RateLimiter:
    def __init__(self, max_per_second=50, max_per_minute=500):
        self._max_sec = max_per_second
        self._max_min = max_per_minute
        self._requests: dict[str, deque] = {}

    def _get_queue(self, api_type: str) -> deque:
        if api_type not in self._requests:
            self._requests[api_type] = deque()
        return self._requests[api_type]

    def _cleanup(self, q: deque) -> None:
        now = time.monotonic()
        while q and q[0] < now - 60:
            q.popleft()

    def record(self, api_type: str = "data") -> None:
        q = self._get_queue(api_type)
        q.append(time.monotonic())

    def is_allowed(self, api_type: str = "data") -> bool:
        q = self._get_queue(api_type)
        self._cleanup(q)
        now = time.monotonic()
        max_sec = 10 if api_type == "order" else self._max_sec
        recent_second = sum(1 for t in q if t > now - 1)
        if recent_second >= max_sec:
            return False
        if len(q) >= self._max_min:
            return False
        return True

    async def acquire(self, api_type: str = "data") -> None:
        while not self.is_allowed(api_type):
            await asyncio.sleep(0.1)
        self.record(api_type)
