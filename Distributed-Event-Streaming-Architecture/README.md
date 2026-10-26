# Distributed Event Streaming & Transactional Outbox Blueprint

An architectural blueprint demonstrating the **Transactional Outbox Pattern**, **Change Data Capture (CDC)**, and **Idempotent Consumer Deduplication** in distributed microservice architectures.

---

## Architectural Mechanics: Eliminating the Dual-Write Bug

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant OrderService as Order Service
    participant LocalDB as PostgreSQL (ACID)
    participant Relay as Debezium CDC / Poller
    participant Kafka as Apache Kafka Broker
    participant BillingConsumer as Billing Microservice (Idempotent)

    Client->>OrderService: POST /orders
    activate OrderService
    Note over OrderService,LocalDB: SINGLE LOCAL TRANSACTION
    OrderService->>LocalDB: INSERT into orders TABLE
    OrderService->>LocalDB: INSERT into outbox TABLE (status = PENDING)
    LocalDB-->>OrderService: Commit Successful
    OrderService-->>Client: 201 Created (Order Placed)
    deactivate OrderService

    Relay->>LocalDB: Tail WAL / Poll PENDING rows
    Relay->>Kafka: Publish OrderPlaced event
    Kafka-->>BillingConsumer: Consume OrderPlaced event
    BillingConsumer->>BillingConsumer: Check Redis Idempotency Key
    alt First Time Event
        BillingConsumer->>BillingConsumer: Execute Ledger Debit & Cache Key
    else Duplicate Network Retry
        BillingConsumer->>BillingConsumer: Drop duplicate event silently
    end
```

---

## Code Simulation

```bash
python3 Web-Applications/Architecture-Blueprints/Distributed-Event-Streaming-Architecture/outbox_pattern_simulator.py
```
Outputs confirmation of the atomic write, Kafka dispatch, and automated duplicate delivery suppression.
