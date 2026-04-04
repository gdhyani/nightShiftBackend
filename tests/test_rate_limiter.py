import asyncio
import pytest
from app.services.rate_limiter import RateLimiter


def test_is_allowed_under_limit():
    rl = RateLimiter(max_per_second=10, max_per_minute=100)
    assert rl.is_allowed("data") is True


def test_is_allowed_over_second_limit():
    rl = RateLimiter(max_per_second=2, max_per_minute=100)
    rl.record("data")
    rl.record("data")
    assert rl.is_allowed("data") is False


async def test_acquire_waits_when_limited():
    rl = RateLimiter(max_per_second=1, max_per_minute=100)
    rl.record("data")
    await asyncio.wait_for(rl.acquire("data"), timeout=2.0)
