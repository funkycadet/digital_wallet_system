from django.core.management.base import BaseCommand
from confluent_kafka.admin import AdminClient, NewTopic
import os


class Command(BaseCommand):
    help = "Create wallet_events topic if it doesn't exist"

    def handle(self, *args, **options):
        admin = AdminClient(
            {"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")}
        )
        topic = NewTopic("wallet_events", num_partitions=3, replication_factor=1)
        fs = admin.create_topics([topic])
        for t, f in fs.items():
            try:
                f.result()  # Wait
                self.stdout.write(self.style.SUCCESS(f"Topic {t} created"))
            except Exception as e:
                if "exists" in str(e):
                    self.stdout.write(self.style.SUCCESS(f"Topic {t} already exists"))
                else:
                    self.stderr.write(f"Failed to create topic {t}: {e}")
