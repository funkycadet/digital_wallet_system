from django.conf.urls import include
from django.urls import re_path as url
from rest_framework.routers import DefaultRouter
from .views import (
    CreateWalletView,
    FundWalletView,
    GetWalletView,
    TransferView,
    WalletTransactionViewset,
)

app_name = "wallet"

router = DefaultRouter()

router.register("transactions", WalletTransactionViewset, basename="transactions")

urlpatterns = [
    url(r"", include(router.urls)),
    url(r"^create/", CreateWalletView.as_view(), name="create"),
    url(r"^(?P<wallet_id>[0-9a-f-]+)/$", GetWalletView.as_view(), name="get_wallet"),
    url(r"^(?P<wallet_id>[0-9a-f-]+)/fund/$", FundWalletView.as_view(), name="fund"),
    url(r"^(?P<wallet_id>[0-9a-f-]+)/transfer/$", TransferView.as_view(), name="transfer"),
]
