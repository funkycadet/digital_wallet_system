from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TransactionEvent


class WalletHistoryView(APIView):
    def get(self, request, wallet_id):
        events = TransactionEvent.objects.filter(wallet_id=wallet_id).order_by(
            "-created_at"
        )
        data = [
            {
                "event_type": e.event_type,
                "amount": str(e.amount),
                "created_at": e.created_at.isoformat(),
                **e.event_data,
            }
            for e in events
        ]
        return Response(data)
