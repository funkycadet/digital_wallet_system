from confluent_kafka import Producer
import json
import uuid
from decouple import config

conf = {
    "bootstrap.servers": config("KAFKA_BOOTSTRAP", "kafka:9092"),
    "client.id": "wallet-service",
}
producer = Producer(conf)


def _delivery_report(err, msg):
    if err:
        print(f"Kafka delivery failed: {err}")


def publish_event(event_type: str, payload: dict):
    topic = "wallet_events"
    key = str(payload.get("wallet_id") or uuid.uuid4())
    value = json.dumps({**payload, "eventType": event_type}).encode()
    producer.produce(topic, key=key, value=value, callback=_delivery_report)
    producer.poll(0)  # non-blocking
