# from confluent_kafka import Consumer, KafkaError
# import json, os, django
# from .models import TransactionEvent
# from decouple import config

# django.setup()


# conf = {
#     "bootstrap.servers": config("KAFKA_BOOTSTRAP", "kafka:9092"),
#     "group.id": "history-service",
#     "auto.offset.reset": "earliest",
# }
# consumer = Consumer(conf)
# consumer.subscribe(["wallet_events"])


# def run_consumer():
#     while True:
#         msg = consumer.poll(1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             if msg.error().code() == KafkaError._PARTITION_EOF:
#                 continue
#             print(msg.error())
#             break

#         payload = json.loads(msg.value().decode())
#         event_type = payload.pop("eventType")

#         # Idempotency via event_id (for TRANSFER_COMPLETED) or transaction_id
#         key = payload.get("event_id") or payload.get("transaction_id")
#         if key and TransactionEvent.objects.filter(transaction_id=key).exists():
#             continue  # already processed

#         TransactionEvent.objects.create(
#             wallet_id=payload["wallet_id"],
#             user_id=payload.get("user_id"),
#             amount=payload["amount"],
#             event_type=event_type,
#             transaction_id=key,
#             event_data=payload,
#         )
