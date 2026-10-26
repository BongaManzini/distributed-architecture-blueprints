#!/usr/bin/env python3
"""
Distributed Zero-Trust API Gateway: Token Bucket & Sliding Window Rate Limiter
Author: Bonga Manzini <contact@bongamanzini.dev>
Domain: Enterprise API Gateway Architecture & Distributed Systems

Implements the Token Bucket algorithm with lazy mathematical refill:
- Allows bursts up to bucket capacity.
- Sustains continuous rate equal to refill rate.
- Returns standardized RFC 6585 RateLimit headers.
"""

import sys
import json
import time
from typing import Dict, Any, Tuple

class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 10, refill_rate_per_sec: float = 2.0):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        # client_id -> {"tokens": float, "last_updated": float}
        self.clients = {}

    def is_allowed(self, client_id: str, tokens_requested: int = 1) -> Tuple[bool, Dict[str, Any]]:
        now = time.time()
        client = self.clients.get(client_id, {"tokens": float(self.capacity), "last_updated": now})

        # Calculate tokens refilled since last access
        elapsed = now - client["last_updated"]
        new_tokens = client["tokens"] + (elapsed * self.refill_rate)
        current_tokens = min(float(self.capacity), new_tokens)

        if current_tokens >= tokens_requested:
            # Consume tokens
            client["tokens"] = current_tokens - tokens_requested
            client["last_updated"] = now
            self.clients[client_id] = client

            headers = {
                "X-RateLimit-Limit": self.capacity,
                "X-RateLimit-Remaining": int(client["tokens"]),
                "X-RateLimit-Reset": int(now + (1.0 / self.refill_rate))
            }
            return True, headers
        else:
            # Reject request (HTTP 429 Too Many Requests)
            client["tokens"] = current_tokens
            client["last_updated"] = now
            self.clients[client_id] = client

            needed = tokens_requested - current_tokens
            retry_after = math.ceil(needed / self.refill_rate)
            headers = {
                "X-RateLimit-Limit": self.capacity,
                "X-RateLimit-Remaining": 0,
                "Retry-After": retry_after
            }
            return False, headers

if __name__ == "__main__":
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate_per_sec=1.0)
    client = "client_corp_mobile_app"

    print("Simulating burst of 5 rapid API calls (Capacity: 3 tokens):")
    for i in range(1, 6):
        allowed, meta = limiter.is_allowed(client, 1)
        status = "200 OK (ALLOWED)" if allowed else "429 TOO MANY REQUESTS (BLOCKED)"
        print(f"Request {i}: {status} -> {meta}")
