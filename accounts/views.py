# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib import messages
from allauth.account.models import EmailAddress
from django.views.decorators.http import require_POST

@require_POST
def resend_verification_view(request):
    email = request.POST.get("email", "").strip()
    # Mensagem genérica para não revelar se o email existe
    generic_msg = "If an account exists for this email, a verification link has been sent."

    if not email:
        messages.info(request, generic_msg)
        return redirect("account_email_verification_sent")      # rota do allauth que por defeito abre o templates/account/verification_sent.html

    try:
        address = EmailAddress.objects.get(email__iexact=email)
        if not address.verified:
            # Reenvia o email de verificação
            address.send_confirmation(request, signup=False)
    except EmailAddress.DoesNotExist:
        pass  # mesmo comportamento: mensagem genérica

    messages.info(request, generic_msg)
    return redirect("account_email_verification_sent")      # rota do allauth que por defeito abre o templates/account/verification_sent.html


@login_required
def account_panel_view(request):
    user = request.user
    # Verifica se o email foi confirmado
    email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
    # Verifica se está no grupo "SemAcesso"
    is_sem_acesso = Group.objects.filter(name="SemAcesso", user=user).exists()

    # Grupo a que o user pertence
    roles = list(request.user.groups.values_list("name", flat=True))
    # esconder "SemAcesso" da lista visível
    visible_roles = [r for r in roles if r != "SemAcesso"]

    return render(request, "account/account_panel.html", {
        "email_verified": email_verified,
        "is_sem_acesso": is_sem_acesso,
        "roles": visible_roles,
        "all_roles": roles,
    })
