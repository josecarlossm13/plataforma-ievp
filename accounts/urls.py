# accounts/urls.py
from django.urls import path
from .views import account_panel_view

urlpatterns = [
    path("", account_panel_view, name="account_panel"),  # /account/
]
