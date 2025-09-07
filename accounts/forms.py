from django import forms
from django.contrib.auth.models import Group


class CustomSignupForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "First name",
            "autofocus": "autofocus",
        }),
    )
    last_name  = forms.CharField(
        label="Last name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Last name",
        })
    )

    def signup(self, request, user):
        # Nome próprio / apelido
        user.first_name = self.cleaned_data.get("first_name").strip()
        user.last_name  = self.cleaned_data.get("last_name").strip()

        # Usa o email como username
        user.username = user.email
        user.save()

        # Adiciona ao grupo "SemAcesso", se existir
        try:
            group = Group.objects.get(name="SemAcesso")
            user.groups.add(group)
        except Group.DoesNotExist:
            pass

        return user
