# core/views.py

from django.views.generic import DetailView, ListView       # Importa classes de visualização genéricas do Django.
from django.shortcuts import render, redirect, get_object_or_404        # Importa funções para renderizar templates e redirecionar.
from django.urls import reverse_lazy
from django.utils.translation import get_language                       # Para obter idioma da interface
from core.models import Term, Area, SubArea, News, Warning, Tutorial, Poster, Thesis, DocumentationLink, ContactInfo, ContactTopMessage                             # Importa o modelo Term,  que contém os dados dos termos.
from django.db.models import Q, Count                                   # Count, Contar o nº de termos nas data tables
from django.db import models
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse                                         # usado para gerar URLs com base no nome dos caminhos
from core.permissions import user_has_access, GroupAccessRequiredMixin
from django.contrib.auth.models import Group, User
from django.utils.timezone import now

# funções para gerar uma stack para usar no botão "voltar"
def update_navigation_stack(request):
    stack = request.session.get('navigation_stack', [])
    current_url = request.get_full_path()

    # Se a pilha estiver vazia ou o topo for diferente da URL atual, adiciona
    if not stack or stack[-1] != current_url:
        # Se o URL atual existir na stack (loop), remove-o antes de re-adicionar
        if current_url in stack:
            stack.remove(current_url)
        stack.append(current_url)

    # Mantém apenas os últimos 10 itens
    request.session['navigation_stack'] = stack[-10:]

def get_back_url(request, fallback_url):
    stack = request.session.get('navigation_stack', [])

    # Remover a página atual do topo
    current_url = request.get_full_path()
    if stack and stack[-1] == current_url:
        stack.pop()

    # Atualizar a stack no request.session
    request.session['navigation_stack'] = stack

    if stack:
        return stack[-1]  # página anterior real
    return fallback_url

class AreaListView(GroupAccessRequiredMixin, ListView):
    model = Area
    template_name = 'core/area_list.html'
    context_object_name = 'areas'
    ordering = ['id']
    #login_url = '/accounts/login/'
    login_url = reverse_lazy("account_login")


    def get(self, request, *args, **kwargs):
        update_navigation_stack(request)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Area.objects.annotate(                                           # Contador de subareas e termos. Distinct -> evita contagens duplicadas.
            subarea_count=Count('subareas', distinct=True),          # conta quantas SubArea estão ligadas à Area
            term_count=Count('subareas__termos', distinct=True)      # conta todos os termos associados às SubArea dessa Area
        ).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['back_url'] = get_back_url(self.request, fallback_url=reverse('home'))

        return context


# View para listar subareas. [pode receber uma (area_id)]
class SubAreaListView(GroupAccessRequiredMixin, ListView):
    model = SubArea
    template_name = 'core/subarea_list.html'
    context_object_name = 'subareas'
    login_url = reverse_lazy("account_login")


    def get(self, request, *args, **kwargs):
        update_navigation_stack(request)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        area_id = self.kwargs.get('area_id')
        # já tem o contador de termos por subarea
        qs = SubArea.objects.select_related('area').annotate(term_count=Count('termos')).order_by('area__id', 'id')
        if area_id:
            qs = qs.filter(area__id=area_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area_id = self.kwargs.get('area_id')
        if area_id:
            context['area'] = Area.objects.filter(id=area_id).first()

        # Botão voltar
        context['back_url'] = get_back_url(self.request, fallback_url=reverse('area-list'))

        return context

# função para detalhes de um termo
@login_required(login_url='/accounts/login/')
def term_detail(request, ref):
    term = get_object_or_404(Term, ref=ref)                     # vai buscar o termo pela ref
    return render(request, 'core/term_detail.html', {'term': term})  # aqui podemos escolher o idioma dos conteúdos se necessário

class TermListView(GroupAccessRequiredMixin, ListView):
    model = Term
    context_object_name = 'terms'
    login_url = reverse_lazy("account_login")

    def get(self, request, *args, **kwargs):
        update_navigation_stack(request)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get("q")
        area_id = self.request.GET.get("area")                  # para o filtro por area da navbar
        subarea_ref = self.kwargs.get('ref')                    # vem da URL
        object_list = self.model.objects.all()

        # Filtra pelo termo de busca, se existir
        if q:
            search_queries = Q()

            # Procura nos campos padrão (sem tradução)
            search_queries |= Q(name__icontains=q)
            search_queries |= Q(description__icontains=q)

            # Procura nas traduções, para todos os idiomas definidos nas settings
            for lang_code, _ in settings.LANGUAGES:
                lang_suffix = lang_code.lower().replace('-', '_')              # resolve o problema do django só reconhecer pt-br, e na base de dados estar pt_br
                search_queries |= Q(**{f'name_{lang_suffix}__icontains': q})
                search_queries |= Q(**{f'description_{lang_suffix}__icontains': q})

            object_list = object_list.filter(search_queries)

        # Filtro por área (menu dropdown da navbar)
        if area_id:
            object_list = object_list.filter(subarea__area__id=area_id)

        # Filtro por subárea (URL)
        if subarea_ref:
            object_list = object_list.filter(subarea__ref=subarea_ref)

        return object_list.order_by('ref')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subarea_ref = self.kwargs.get('ref')
        subarea = None
        if subarea_ref:
            subarea = SubArea.objects.select_related('area').filter(ref=subarea_ref).first()#############
            context['subarea'] = subarea
            context['subarea_ref'] = subarea_ref
        else:
            # Se não há subarea, evita usar esses campos no template
            context['subarea_ref'] = None
            context['subarea'] = None

        # Adiciona o valor da área selecionada (se algum)
        context['selected_area_id'] = self.request.GET.get('area')
        context['search_query'] = self.request.GET.get('q', '')

        # fallback dinâmico com área da subárea
        if subarea and subarea.area:
            fallback_url = reverse('subarea-list-by-area', args=[subarea.area.id])
        else:
            fallback_url = reverse('subarea-list')

        context['back_url'] = get_back_url(self.request, fallback_url=fallback_url)

        return context


class TermDetailView(GroupAccessRequiredMixin, DetailView):
    model = Term
    context_object_name = 'term'
    login_url = reverse_lazy("account_login")

    def get(self, request, *args, **kwargs):
        update_navigation_stack(request)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        ref = self.kwargs.get('ref')
        return get_object_or_404(Term, ref=ref)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fallback_url preservando filtros
        # Usar a função para obter o back_url (botão "voltar")
        subarea_ref = self.request.GET.get('ref')
        query = self.request.GET.get('q')
        area_id = self.request.GET.get('area')

        if subarea_ref:
            fallback = reverse('term-list-by-subarea', kwargs={'ref': subarea_ref})
        else:
            fallback = reverse('term-list')

        query_params = []
        if query:
            query_params.append(f'q={query}')
        if area_id:
            query_params.append(f'area={area_id}')

        if query_params:
            fallback += '?' + '&'.join(query_params)

        # Conteúdo traduzido, etc.
        # Define o idioma do conteúdo a partir da query string ou da interface
        content_language = self.request.GET.get('language') or get_language()
        query = self.request.GET.get('q', '')

        ######### added to IEVP #########
        published_field = f'published_at_{content_language}'
        ###################################################
        term = context['term']
        # Campos traduzidos dinamicamente
        name_field = f'name_{content_language}'
        description_field = f'description_{content_language}'
        extra_field = f'extra_{content_language}'
        # Atribui os valores traduzidos ao contexto
        context['term_name'] = getattr(term, name_field, term.name)
        context['term_description'] = getattr(term, description_field, term.description)
        context['term_extra'] = getattr(term, extra_field, term.extra)
        context['content_language'] = content_language
        context['subarea'] = term.subarea
        # Adiciona filtros ao contexto para manter os valores no link de retorno
        context['query'] = query
        context['selected_area_id'] = area_id
        context['subarea_ref'] = subarea_ref
        # Definir back_url usando a stack de navegação, ou fallback com filtros
        context['back_url'] = get_back_url(self.request, fallback_url=fallback)
        ######### added to IEVP #############
        context['term_published_at'] = getattr(term, published_field, None)

        return context

# homepage
def home(request):
    # listas vazias para evitar erros com users anonimos
    context = {
        'news': [],
        'warnings': [],
        'user_status': 'anonymous',  # default
        'posters': Poster.objects.filter(active=True).order_by('position','-id')
    }

    # verificação para mostrar o botão quick access do painel admin
    context['is_admin_or_gestor'] = (
            request.user.is_authenticated
            and (
                    request.user.is_superuser
                    or request.user.groups.filter(name__in=['Admin', 'Gestor']).exists()
            )
    )

    if request.user.is_authenticated:
        if not request.user.emailaddress_set.filter(verified=True).exists():
            context['user_status'] = 'email_unverified'
        elif Group.objects.filter(name="SemAcesso", user=request.user).exists():
            context['user_status'] = 'awaiting_approval'
        else:
            context['user_status'] = 'approved'
            # Só carrega conteúdos se tiver email verificado e for aprovado
            context['news'] = News.objects.filter(
                active=True
            ).filter(
                models.Q(start_date__lte=now()) | models.Q(start_date__isnull=True),
                models.Q(end_date__gte=now()) | models.Q(end_date__isnull=True)
            ).order_by('position','-created_at')

            context['warnings'] = Warning.objects.filter(
                active=True
            ).filter(
                models.Q(show_from__lte=now()) | models.Q(show_from__isnull=True),
                models.Q(hide_after__gte=now()) | models.Q(hide_after__isnull=True)
            ).order_by('position','-created_at')

    # Se aprovado mostra os últimos termos adicionados + atalhos
    context['latest_terms'] = []
    context['show_quick'] = False

    if context['user_status'] == 'approved':
        context['latest_terms'] = Term.objects.order_by('-created')[:6]
        context['show_quick'] = True

    return render(request, 'home.html', context)


# lista (queryset) de todos os tutoriais ativos, ordenados por posição, com restrição dependendo do grupo do user
@user_has_access()
def tutorial_view(request):
    # Verifica se o user é Admin, Gestor ou Superuser
    is_admin_or_gestor_or_superuser = request.user.groups.filter(name__in=['Admin', 'Gestor']).exists() or request.user.is_superuser

    # Se o user for Admin, Gestor ou Superuser, mostra todos os tutoriais, caso contrário, só os não restritos
    if is_admin_or_gestor_or_superuser:
        tutorials = Tutorial.objects.filter(active=True).order_by('position')
    else:
        tutorials = Tutorial.objects.filter(active=True, restricted=False).order_by('position')  # Exibe apenas os tutoriais não restritos

    return render(request, 'core/tutorial.html', {'tutorials': tutorials, 'is_admin_or_gestor_or_superuser': is_admin_or_gestor_or_superuser})


def poster_view(request):
    posters = Poster.objects.filter(active=True).order_by('position','-id')
    return render(request, "core/poster.html", {"posters": posters})

@user_has_access()
def thesis_view(request):
    thesis = Thesis.objects.filter(active=True).first()
    return render(request, "core/thesis.html", {"thesis": thesis})

@user_has_access()
def documentation_view(request):
    links = DocumentationLink.objects.filter(active=True).order_by('position','name')
    return render(request, "core/documentation.html", {"links": links})


def contacts_view(request):
    top_messages = ContactTopMessage.objects.filter(
        active=True
    ).filter(
        models.Q(show_from__lte=now()) | models.Q(show_from__isnull=True),
        models.Q(hide_after__gte=now()) | models.Q(hide_after__isnull=True),
    ).order_by("position", "-id")

    contacts = ContactInfo.objects.filter(active=True).order_by("position")
    return render(request, "core/contacts.html", {
        "top_messages": top_messages,
        "contacts": contacts,
    })

