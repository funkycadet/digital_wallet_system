from django_filters import rest_framework as filters
from .models import WalletTransaction


class WalletTransactionFilter(filters.FilterSet):
    on = filters.DateFilter(field_name="date_created", lookup_expr="date")
    before = filters.DateFilter(field_name="date_created", lookup_expr="lt")
    after = filters.DateFilter(field_name="date_created", lookup_expr="gt")
    start = filters.DateFilter(field_name="date_created", lookup_expr="gte")
    end = filters.DateFilter(field_name="date_created", lookup_expr="lte")

    class Meta:
        model = WalletTransaction
        fields = ["on", "before", "after", "start", "end", "type", "status"]
