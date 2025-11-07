from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Wallet, WalletTransaction


class UsersAdmin(UserAdmin):
    pass


admin.site.register(User, UsersAdmin)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
