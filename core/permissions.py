# core/permissions.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


# Decorador: Permite acesso apenas a utilizadores autenticados que não estão no grupo 'SemAcesso'
# Redireciona se não tiver acesso.
def user_has_access(redirect_url='/'):

    def check(user):
        return user.is_authenticated and not user.groups.filter(name="SemAcesso").exists()

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            elif not check(request.user):
                return redirect(redirect_url)  # redireciona em vez de 403
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    return decorator

# Mixin: bloqueia acesso a utilizadores no grupo 'SemAcesso' e redireciona para a home.
class GroupAccessRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and not user.groups.filter(name="SemAcesso").exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # redireciona para login
        return redirect(reverse('home'))  # user autenticado mas sem permissão

