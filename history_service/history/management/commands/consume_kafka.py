# import time
# import json
# import django
# from django.core.management.base import BaseCommand
# from confluent_kafka import Consumer, KafkaError

# django.setup()
# from history.models import TransactionEvent


# class Command(BaseCommand):
#     help = "Consume wallet_events from Kafka"

#     def handle(self, *args, **options):
#         conf = {
#             "bootstrap.servers": "kafka:9092",
#             "group.id": "history-service",
#             "auto.offset.reset": "earliest",
#             "enable.auto.commit": False,
#         }

#         consumer = Consumer(conf)
#         consumer.subscribe(["wallet_events"])

#         self.stdout.write("Kafka consumer started – waiting for messages…")

#         while True:
#             msg = consumer.poll(1.0)
#             if msg is None:
#                 continue
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     continue
#                 self.stderr.write(f"Kafka error: {msg.error()}")
#                 time.sleep(5)
#                 continue

#             try:
#                 payload = json.loads(msg.value().decode())
#                 event_type = payload.pop("eventType", "UNKNOWN")
#                 key = payload.get("event_id") or payload.get("transaction_id")

#                 # Idempotency
#                 if key and TransactionEvent.objects.filter(transaction_id=key).exists():
#                     consumer.commit(asynchronous=True)
#                     continue

#                 TransactionEvent.objects.create(
#                     wallet_id=payload["wallet_id"],
#                     user_id=payload.get("user_id", ""),
#                     amount=payload["amount"],
#                     event_type=event_type,
#                     transaction_id=key,
#                     event_data=payload,
#                 )
#                 consumer.commit(asynchronous=True)
#                 self.stdout.write(f"Processed {event_type}")
#             except Exception as e:
#                 self.stderr.write(f"Processing failed: {e}")
#                 time.sleep(2)  # back‑off


# history_service/history/management/commands/consume_kafka.py
import time
import json
import os
import django
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError

django.setup()
from history.models import TransactionEvent  # noqa: E402


class Command(BaseCommand):
    help = "Consume wallet_events from Kafka (idempotent, resilient)"

    def handle(self, *args, **options):
        bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
        conf = {
            "bootstrap.servers": bootstrap,
            "group.id": "history-service",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            # Keep connection alive even if broker restarts
            "reconnect.backoff.ms": 1000,
            "reconnect.backoff.max.ms": 10000,
        }

        consumer = Consumer(conf)
        consumer.subscribe(["wallet_events"])

        self.stdout.write(
            self.style.SUCCESS("Kafka consumer started – waiting for messages…")
        )

        # Simple file‑based liveness probe (Docker healthcheck reads this)
        liveness_file = "/tmp/consumer_alive"
        open(liveness_file, "a").close()

        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    # Refresh liveness file every poll
                    open(liveness_file, "a").close()
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    self.stderr.write(f"Kafka error: {msg.error()}")
                    time.sleep(5)
                    continue

                payload = json.loads(msg.value().decode())
                event_type = payload.pop("eventType", "UNKNOWN")
                key = payload.get("event_id") or payload.get("transaction_id")

                # Idempotency
                if key and TransactionEvent.objects.filter(transaction_id=key).exists():
                    consumer.commit(asynchronous=True)
                    continue

                TransactionEvent.objects.create(
                    wallet_id=payload["wallet_id"],
                    user_id=payload.get("user_id", ""),
                    amount=payload["amount"],
                    event_type=event_type,
                    transaction_id=key,
                    event_data=payload,
                )
                consumer.commit(asynchronous=True)
                self.stdout.write(f"Processed {event_type}")

            except Exception as e:
                self.stderr.write(f"Processing failed: {e}")
                time.sleep(2)
