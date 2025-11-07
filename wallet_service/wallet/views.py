from django.db import transaction
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import User, Wallet, WalletTransaction
from .serializers import FundSerializer, TransferSerializer, WalletTransactionSerializer
from .filters import WalletTransactionFilter
from .producers import publish_event
import uuid


class CreateWalletView(APIView):
    def post(self, request):
        user_id = request.data["user_id"]
        user = User.objects.get(id=user_id)
        wallet = Wallet.objects.create(user_id=user)
        publish_event(
            "WALLET_CREATED",
            {
                "wallet_id": str(wallet.id),
                "user_id": user_id,
            },
        )
        return Response({"wallet_id": str(wallet.id)}, status=status.HTTP_201_CREATED)


class GetWalletView(APIView):
    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(pk=wallet_id)
            return Response({"wallet_id": str(wallet.id), "balance": wallet.balance, "version": wallet.version}, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)


class FundWalletView(APIView):
    @transaction.atomic
    def post(self, request, wallet_id):
        ser = FundSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount = ser.validated_data["amount"]
        expected_version = ser.validated_data["version"]

        # Optimistic locking: Update balance and increment version only if the version matches
        rows_affected = Wallet.objects.filter(
            pk=wallet_id, version=expected_version
        ).update(balance=F("balance") + amount, version=F("version") + 1)

        if rows_affected == 0:
            # If no rows were affected, it means the version was stale or wallet_id was invalid
            # We need to check if the wallet exists to differentiate between stale data and invalid ID
            if not Wallet.objects.filter(pk=wallet_id).exists():
                return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Stale data. Please retry with the latest version."}, status=status.HTTP_409_CONFLICT)

        # Retrieve the updated wallet to get the new balance and version
        wallet = Wallet.objects.get(pk=wallet_id)

        tx = WalletTransaction.objects.create(wallet=wallet, amount=amount, type="FUND")
        publish_event(
            "WALLET_FUNDED",
            {
                "wallet_id": str(wallet.id),
                "user_id": str(wallet.user_id), # Ensure user_id is a string
                "amount": str(amount),
                "transaction_id": str(tx.id),
            },
        )
        return Response({"balance": wallet.balance, "version": wallet.version}, status=status.HTTP_200_OK)


class TransferView(APIView):
    @transaction.atomic
    def post(self, request, wallet_id):
        from_wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
        ser = TransferSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        to_wallet = Wallet.objects.select_for_update().get(
            pk=ser.validated_data["to_wallet_id"]
        )
        amount = ser.validated_data["amount"]

        if from_wallet.balance < amount:
            raise serializers.ValidationError("Insufficient funds")

        # Optimistic lock check
        expected_version = int(request.headers.get("X-Version", from_wallet.version))
        if expected_version != from_wallet.version:
            return Response({"error": "Stale data"}, status=409)

        # Update both
        from_wallet.balance -= amount
        to_wallet.balance += amount
        from_wallet.version += 1
        to_wallet.version += 1
        Wallet.objects.bulk_update([from_wallet, to_wallet], ["balance", "version"])

        # Record two tx
        tx_out = WalletTransaction.objects.create(
            wallet=from_wallet, amount=-amount, type="TRANSFER_OUT"
        )
        tx_in = WalletTransaction.objects.create(
            wallet=to_wallet, amount=amount, type="TRANSFER_IN"
        )

        event_id = str(uuid.uuid4())
        publish_event(
            "TRANSFER_COMPLETED",
            {
                "event_id": event_id,
                "from_wallet_id": str(from_wallet.id),
                "to_wallet_id": str(to_wallet.id),
                "amount": str(amount),
                "from_tx_id": str(tx_out.id),
                "to_tx_id": str(tx_in.id),
            },
        )
        return Response(
            {
                "from_balance": from_wallet.balance,
                "to_balance": to_wallet.balance,
                "version": from_wallet.version,
            },
            status=status.HTTP_200_OK,
        )


class WalletTransactionViewset(ModelViewSet):
    queryset = WalletTransaction.objects.all()
    serializer_class = WalletTransactionSerializer
    filterset_class = WalletTransactionFilter
