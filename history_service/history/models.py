from django.db import models
import uuid


class TransactionEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_id = models.UUIDField(db_index=True)
    user_id = models.CharField(max_length=100, db_index=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    event_type = models.CharField(max_length=30)  # WALLET_CREATED, WALLET_FUNDED, …
    transaction_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_data = models.JSONField(default=dict)
