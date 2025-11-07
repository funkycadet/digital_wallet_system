from django.urls import include, re_path as url
from rest_framework.routers import DefaultRouter
from .views import WalletHistoryView

app_name = "history"

router = DefaultRouter()

urlpatterns = [
    url(r"", include(router.urls)),
    url(r"history/", WalletHistoryView.as_view(), name="history"),
]
