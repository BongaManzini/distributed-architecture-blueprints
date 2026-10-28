# Distributed Systems Architecture Blueprints ️

Hi! These are two working Python reference architectures I built to understand how high-traffic web applications prevent data loss and survive sudden traffic spikes.

---

## What Is Inside This Folder

```
Architecture-Blueprints/
├── Distributed-Event-Streaming-Architecture/
│  ├── outbox_pattern_simulator.py   # Transactional Outbox Pattern & event deduplication
│  └── README.md
│
└── Zero-Trust-API-Gateway/
    ├── token_bucket_rate_limiter.py     # Token Bucket rate limiter in Python
    └── README.md
```

---

## The Two Blueprints Explained Simply

### 1. Transactional Outbox Pattern (`outbox_pattern_simulator.py`)
- **The Problem It Solves**: In microservice architectures, when a customer places an order, your app must save the order to the database AND send a message to a queue (like Kafka or RabbitMQ). If the network dies right after saving to the database, the message is never sent, and the customer order gets lost.
- **How This Fixes It**: Instead of trying to update two different systems at once, the app writes the order AND the message into the same SQL database in a single transaction. A background worker then safely picks up the message and sends it. If it fails, it retries until it succeeds.
- **Deduplication**: Uses idempotency keys so that if a message is delivered twice, downstream services ignore the duplicate.

### 2. Token Bucket Rate Limiter (`token_bucket_rate_limiter.py`)
- **The Problem It Solves**: If a bot or thousands of users suddenly spam an API with requests at the exact same second, the server crashes.
- **How This Fixes It**: Think of a bucket that holds tokens. Every time a request comes in, it takes a token. Tokens are added back smoothly over time (e.g. 10 tokens per second). If the bucket is empty, the server returns an HTTP 429 'Too Many Requests' error with a `Retry-After` header instead of crashing.

---

## How to Run These Scripts

```bash
# 1. Run the Outbox Pattern Simulator
python3 Distributed-Event-Streaming-Architecture/outbox_pattern_simulator.py

# 2. Run the Rate Limiter Simulator
python3 Zero-Trust-API-Gateway/token_bucket_rate_limiter.py
```

---

## Contributing & Pull Requests

Feedback, tests, and PRs are always welcome!
1. Fork this repository
2. Create your branch (`git checkout -b feature/redis-backend`)
3. Commit with clear comments
4. Submit a Pull Request!
