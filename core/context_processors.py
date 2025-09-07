# core/context_processors.py
"""
Uso: Funções definidas aqui retornam dicionários com variáveis
que ficam automaticamente disponíveis em todos os templates
(ou em templates que usem um base.html que herde o contexto global),
desde que estejam registadas em settings.TEMPLATES[0]['OPTIONS']['context_processors'].
"""

from .models import Area

# Filtrar na navbar por area (garantir que todas as views que usam o base.html enviem as áreas no contexto)
def areas_dropdown(request):
    """
    Retorna todas as áreas (ordenadas por id) para popular o menu de seleção na navbar.
    """
    return {
        'all_areas': Area.objects.all().order_by('id')
    }

# Para exibir certas funcionalidades na front end, tal como o Painel Admin.
def user_permissions(request):
    """
    Retorna um booleano indicando se o utilizador atual é Admin, Gestor ou Superuser,
    para condicionar exibição de funcionalidades no frontend.
    """
    is_admin_or_gestor = request.user.groups.filter(name__in=['Admin', 'Gestor']).exists() or request.user.is_superuser
    return {'is_admin_or_gestor': is_admin_or_gestor}
