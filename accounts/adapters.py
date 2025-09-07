# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class AccountAdapter(DefaultAccountAdapter):
    def get_password_change_redirect_url(self, request):
        # depois de mudar a password -> account panel
        return reverse("account_panel")