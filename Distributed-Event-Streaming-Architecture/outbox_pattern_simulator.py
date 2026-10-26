#!/usr/bin/env python3
"""
Distributed Systems: Transactional Outbox Pattern & Idempotent Consumer Engine
Author: Bonga Manzini <contact@bongamanzini.dev>
Domain: Enterprise Distributed Systems & Microservice Architecture

Demonstrates guaranteed at-least-once event delivery and exactly-once processing:
1. Atomically commits order entity and outbox event in a single database transaction (eliminating dual-write bugs).
2. Background message relay (simulated Debezium CDC) publishes outbox messages to Kafka.
3. Idempotent consumer deduplicates messages using an atomic idempotency key cache.
"""

import sys
import json
import time
import uuid
from typing import Dict, Any, List

class MockRelationalDatabase:
    def __init__(self):
        self.orders_table = {}
        self.outbox_table = {}

    def execute_transactional_write(self, order_id: str, order_payload: Dict[str, Any], event_type: str) -> str:
        """
        Atomically writes to orders table AND outbox table in one local ACID transaction.
        """
        event_id = str(uuid.uuid4())
        # 1. Update domain aggregate
        self.orders_table[order_id] = order_payload
        # 2. Write to outbox table
        self.outbox_table[event_id] = {
            "event_id": event_id,
            "aggregate_id": order_id,
            "event_type": event_type,
            "payload": order_payload,
            "status": "PENDING",
            "created_at": time.time()
        }
        return event_id

class MessageRelayWorker:
    def __init__(self, db: MockRelationalDatabase):
        self.db = db
        self.published_events = []

    def poll_and_publish(self) -> List[Dict[str, Any]]:
        batch = []
        for event_id, item in list(self.db.outbox_table.items()):
            if item["status"] == "PENDING":
                # Simulate publishing to Kafka topic
                batch.append(item)
                item["status"] = "PUBLISHED"
                self.published_events.append(item)
        return batch

class IdempotentEventConsumer:
    def __init__(self):
        self.processed_event_ids = set()
        self.ledger_balance = 0

    def consume_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event["event_id"]
        # Idempotency check
        if event_id in self.processed_event_ids:
            return {
                "status": "DUPLICATE_IGNORED",
                "event_id": event_id,
                "message": "Event already processed. Idempotency key matched in Redis cache."
            }

        # Process business logic
        amount = event["payload"].get("amount", 0)
        self.ledger_balance += amount
        self.processed_event_ids.add(event_id)

        return {
            "status": "SUCCESSFULLY_PROCESSED",
            "event_id": event_id,
            "new_ledger_balance": self.ledger_balance
        }

if __name__ == "__main__":
    db = MockRelationalDatabase()
    relay = MessageRelayWorker(db)
    consumer = IdempotentEventConsumer()

    # 1. Place an order (Atomic Local ACID Transaction)
    order_id = "ORD-ZA-7718"
    evt_id = db.execute_transactional_write(
        order_id=order_id,
        order_payload={"item": "MacBook Pro", "amount": 34999.00, "customer": "jdoe@corp.internal"},
        event_type="ORDER_PLACED"
    )

    # 2. Message Relay polls outbox and transmits to Kafka
    messages_dispatched = relay.poll_and_publish()

    # 3. Consumer processes message
    result_1 = consumer.consume_event(messages_dispatched[0])
    # 4. Consumer receives duplicate delivery from network retry
    result_2 = consumer.consume_event(messages_dispatched[0])

    print(json.dumps({
        "order_aggregate_committed": db.orders_table[order_id],
        "first_delivery": result_1,
        "retry_duplicate_delivery": result_2
    }, indent=2))
