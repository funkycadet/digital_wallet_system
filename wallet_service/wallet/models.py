import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user_id = models.CharField(max_length=100, db_index=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    balance = models.DecimalField(
        max_digits=19, decimal_places=4, default=0, validators=[MinValueValidator(0)]
    )
    version = models.BigIntegerField(default=0)  # optimistic lock
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user_id"])]


class WalletTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.CharField(
        max_length=20,
        choices=[
            ("FUND", "FUND"),
            ("TRANSFER_OUT", "TRANSFER_OUT"),
            ("TRANSFER_IN", "TRANSFER_IN"),
        ],
    )
    status = models.CharField(
        max_length=20,
        default="COMPLETED",
        choices=[("COMPLETED", "COMPLETED"), ("FAILED", "FAILED")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
