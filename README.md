# Software Engineering & Distributed Architecture Blueprints

Enterprise software architecture blueprints, distributed systems patterns, and resilience designs engineered for high-concurrency cloud environments.

---

## Directory Index

```
Architecture-Blueprints/
├── Distributed-Event-Streaming-Architecture/
│   ├── outbox_pattern_simulator.py      # Transactional outbox & idempotent consumer deduplication
│   └── README.md
│
├── Zero-Trust-API-Gateway/
│   ├── token_bucket_rate_limiter.py     # Distributed Token Bucket & RFC 6585 rate limiting
│   └── README.md
│
├── Suggested-Projects-and-Roadmaps/     # CQRS, Event Sourcing, Saga orchestrator designs
│   └── README.md
│
└── README.md                            # This overview
```

---

## Design Principles Applied

- **Guaranteed At-Least-Once Delivery:** Eliminating dual-write vulnerabilities between transactional databases and messaging brokers via the Transactional Outbox Pattern and Change Data Capture (CDC).
- **Idempotency & Deduplication:** Redis-backed idempotency key caching preventing duplicate state mutation upon network retries.
- **Traffic Shaping & Resilience:** Token bucket rate limiting protecting downstream microservices from denial of service and traffic spikes.
