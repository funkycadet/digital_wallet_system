from rest_framework import serializers
from .models import User, Wallet, WalletTransaction


class FundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=19, decimal_places=4)
    version = serializers.IntegerField(min_value=0)


class TransferSerializer(serializers.Serializer):
    to_wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=19, decimal_places=4)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = "__all__"
