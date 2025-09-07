# core/admin.py
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from modeltranslation.admin import TranslationAdmin                         # Importa o TranslationAdmin, uma classe fornecida pelo pacote django-modeltranslation para facilitar a tradução de campos de modelos do Django na interface de administração
from reversion.admin import VersionAdmin
from .models import Area, SubArea, Term, News, Warning, Tutorial, Poster, Thesis, DocumentationLink, ContactInfo, ContactTopMessage
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

# Define as colunas de importação/exportação para o modelo Area (tem que ficar antes do AreaAdmin)
class AreaResource(resources.ModelResource):
    class Meta:
        model = Area
        import_id_fields = ['id']                                           # Define o campo que será usado como identificador único durante a importação
        fields = ['id', 'name_en', 'name_pt', 'name_pt_br', 'name_es', 'name_sq', 'name_ar', 'name_hy',
                  'name_bs', 'name_bg', 'name_zh_hans', 'name_hr', 'name_da', 'name_nl', 'name_et', 'name_fi', 'name_fr',
                  'name_de', 'name_ka', 'name_el', 'name_hu', 'name_is', 'name_ga', 'name_it', 'name_ja', 'name_ko',
                  'name_lv', 'name_lt', 'name_mk', 'name_nb', 'name_pl', 'name_ro', 'name_ru', 'name_sr', 'name_sk',
                  'name_sl', 'name_sv', 'name_tr', 'name_uk']               # Define os campos a serem importados/exportados

# Define as colunas de importação/exportação para o modelo SubArea
class SubAreaResource(resources.ModelResource):
    class Meta:
        model = SubArea
        import_id_fields = ['ref']
        fields = ['ref', 'area', 'id', 'name_en', 'name_pt', 'name_pt_br', 'name_es', 'name_sq', 'name_ar', 'name_hy',
                  'name_bs', 'name_bg', 'name_zh_hans', 'name_hr', 'name_da', 'name_nl', 'name_et', 'name_fi', 'name_fr',
                  'name_de', 'name_ka', 'name_el', 'name_hu', 'name_is', 'name_ga', 'name_it', 'name_ja', 'name_ko',
                  'name_lv', 'name_lt', 'name_mk', 'name_nb', 'name_pl', 'name_ro', 'name_ru', 'name_sr', 'name_sk',
                  'name_sl', 'name_sv', 'name_tr', 'name_uk']


@admin.register(Area)                                                   # Regista o modelo Area na interface de administração do Django, permitindo a sua gestão através do painel de administração.
class AreaAdmin(VersionAdmin,TranslationAdmin, ImportExportModelAdmin):                    # Classe AreaAdmin herda de TranslationAdmin, permitindo que a interface de administração suporte a tradução dos campos do modelo Area.
    list_display = ['id', 'name']                                       # Define os campos do modelo que serão exibidos na lista de objetos na interface de administração.
    search_fields = ['name']                                            # Permite adicionar uma barra de pesquisa na interface de administração, onde os utilizadores podem procurar por 'name'.
    resource_classes = [AreaResource]                                   # Adiciona a classe de recurso para importação, para definir as colunas a importar.

@admin.register(SubArea)                                                # Regista o modelo SubArea na interface de administração do Django, permitindo a sua gestão através do painel de administração.
class SubAreaAdmin(VersionAdmin, TranslationAdmin, ImportExportModelAdmin):                # Classe SubAreaAdmin herda de TranslationAdmin, permitindo que a interface de administração suporte a tradução dos campos do modelo SubArea.
    list_display = ['ref','id', 'name', 'area']                         # Define os campos do modelo que serão exibidos na lista de objetos na interface de administração.
    list_filter = ['area']                                              # Adiciona um filtro na interface de administração, permitindo filtrar os objetos com base na 'area' associada.
    search_fields = ['name']                                            # Permite adicionar uma barra de pesquisa na interface de administração, onde os utilizadores podem procurar por 'name'.
    resource_classes = [SubAreaResource]

    # Ordenar as opções do ForeignKey 'area' no painel de administração, menu drop down
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'area':
            kwargs['queryset'] = Area.objects.all().order_by('id')      # Ordena as Áreas pelo 'id'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TermResource(resources.ModelResource):

    def before_save_instance(self, instance, row, **kwargs):
        for field in ['name_en', 'name_pt', 'name_pt_br', 'name_es', 'name_sq', 'name_ar', 'name_hy', 'name_bs',
                      'name_bg', 'name_zh_hans', 'name_hr', 'name_da', 'name_nl', 'name_et', 'name_fi', 'name_fr',
                      'name_de', 'name_ka', 'name_el', 'name_hu', 'name_is', 'name_ga', 'name_it', 'name_ja', 'name_ko',
                      'name_lv', 'name_lt', 'name_mk', 'name_nb', 'name_pl', 'name_ro', 'name_ru', 'name_sr', 'name_sk',
                      'name_sl', 'name_sv', 'name_tr', 'name_uk']:
            if getattr(instance, field) == '':
                setattr(instance, field, None)

    def before_import(self, dataset, **kwargs):
                                                            # mimic a 'dynamic field' - i.e. append field which exists on Book model, but not in dataset
        dataset.headers.append('subarea')
        dataset.headers.append('ref')
        super().before_import(dataset, **kwargs)

    def before_import_row(self, row, **kwargs):
        iev_ref = row['ref'].strip()
        #area_id = iev_ref.split('-')[0]                    # 301
        subarea_ref = iev_ref.rsplit('-', 1)[0]             # 301-02
        term_id = iev_ref.rsplit('-', 1)[-1]                # 01
        row['id'] = term_id
        row['subarea'] = subarea_ref
        row['ref'] = iev_ref

    class Meta:
        model = Term
        import_id_fields = ['ref']

        fields = ['ref', 'subarea', 'id',
            'name_en', 'description_en', 'source_en', 'extra_en',
            'name_pt', 'description_pt', 'source_pt', 'extra_pt',
            'name_pt_br', 'description_pt_br', 'source_pt_br', 'extra_pt_br',
            'name_es', 'description_es', 'source_es', 'extra_es',
            'name_sq', 'description_sq', 'source_sq', 'extra_sq',
            'name_ar', 'description_ar', 'source_ar', 'extra_ar',
            'name_hy', 'description_hy', 'source_hy', 'extra_hy',
            'name_bs', 'description_bs', 'source_bs', 'extra_bs',
            'name_bg', 'description_bg', 'source_bg', 'extra_bg',
            'name_zh_hans', 'description_zh_hans', 'source_zh_hans', 'extra_zh_hans',
            'name_hr', 'description_hr', 'source_hr', 'extra_hr',
            'name_da', 'description_da', 'source_da', 'extra_da',
            'name_nl', 'description_nl', 'source_nl', 'extra_nl',
            'name_et', 'description_et', 'source_et', 'extra_et',
            'name_fi', 'description_fi', 'source_fi', 'extra_fi',
            'name_fr', 'description_fr', 'source_fr', 'extra_fr',
            'name_de', 'description_de', 'source_de', 'extra_de',
            'name_ka', 'description_ka', 'source_ka', 'extra_ka',
            'name_el', 'description_el', 'source_el', 'extra_el',
            'name_hu', 'description_hu', 'source_hu', 'extra_hu',
            'name_is', 'description_is', 'source_is', 'extra_is',
            'name_ga', 'description_ga', 'source_ga', 'extra_ga',
            'name_it', 'description_it', 'source_it', 'extra_it',
            'name_ja', 'description_ja', 'source_ja', 'extra_ja',
            'name_ko', 'description_ko', 'source_ko', 'extra_ko',
            'name_lv', 'description_lv', 'source_lv', 'extra_lv',
            'name_lt', 'description_lt', 'source_lt', 'extra_lt',
            'name_mk', 'description_mk', 'source_mk', 'extra_mk',
            'name_nb', 'description_nb', 'source_nb', 'extra_nb',
            'name_pl', 'description_pl', 'source_pl', 'extra_pl',
            'name_ro', 'description_ro', 'source_ro', 'extra_ro',
            'name_ru', 'description_ru', 'source_ru', 'extra_ru',
            'name_sr', 'description_sr', 'source_sr', 'extra_sr',
            'name_sk', 'description_sk', 'source_sk', 'extra_sk',
            'name_sl', 'description_sl', 'source_sl', 'extra_sl',
            'name_sv', 'description_sv', 'source_sv', 'extra_sv',
            'name_tr', 'description_tr', 'source_tr', 'extra_tr',
            'name_uk', 'description_uk', 'source_uk', 'extra_uk',
            'image',
            'created', 'updated'
            ]

        import_order = ['ref', 'subarea', 'id',
            'name_en', 'description_en', 'source_en', 'extra_en',
            'name_pt', 'description_pt', 'source_pt', 'extra_pt',
            'name_pt_br', 'description_pt_br', 'source_pt_br', 'extra_pt_br',
            'name_es', 'description_es', 'source_es', 'extra_es',
            'name_sq', 'description_sq', 'source_sq', 'extra_sq',
            'name_ar', 'description_ar', 'source_ar', 'extra_ar',
            'name_hy', 'description_hy', 'source_hy', 'extra_hy',
            'name_bs', 'description_bs', 'source_bs', 'extra_bs',
            'name_bg', 'description_bg', 'source_bg', 'extra_bg',
            'name_zh_hans', 'description_zh_hans', 'source_zh_hans', 'extra_zh_hans',
            'name_hr', 'description_hr', 'source_hr', 'extra_hr',
            'name_da', 'description_da', 'source_da', 'extra_da',
            'name_nl', 'description_nl', 'source_nl', 'extra_nl',
            'name_et', 'description_et', 'source_et', 'extra_et',
            'name_fi', 'description_fi', 'source_fi', 'extra_fi',
            'name_fr', 'description_fr', 'source_fr', 'extra_fr',
            'name_de', 'description_de', 'source_de', 'extra_de',
            'name_ka', 'description_ka', 'source_ka', 'extra_ka',
            'name_el', 'description_el', 'source_el', 'extra_el',
            'name_hu', 'description_hu', 'source_hu', 'extra_hu',
            'name_is', 'description_is', 'source_is', 'extra_is',
            'name_ga', 'description_ga', 'source_ga', 'extra_ga',
            'name_it', 'description_it', 'source_it', 'extra_it',
            'name_ja', 'description_ja', 'source_ja', 'extra_ja',
            'name_ko', 'description_ko', 'source_ko', 'extra_ko',
            'name_lv', 'description_lv', 'source_lv', 'extra_lv',
            'name_lt', 'description_lt', 'source_lt', 'extra_lt',
            'name_mk', 'description_mk', 'source_mk', 'extra_mk',
            'name_nb', 'description_nb', 'source_nb', 'extra_nb',
            'name_pl', 'description_pl', 'source_pl', 'extra_pl',
            'name_ro', 'description_ro', 'source_ro', 'extra_ro',
            'name_ru', 'description_ru', 'source_ru', 'extra_ru',
            'name_sr', 'description_sr', 'source_sr', 'extra_sr',
            'name_sk', 'description_sk', 'source_sk', 'extra_sk',
            'name_sl', 'description_sl', 'source_sl', 'extra_sl',
            'name_sv', 'description_sv', 'source_sv', 'extra_sv',
            'name_tr', 'description_tr', 'source_tr', 'extra_tr',
            'name_uk', 'description_uk', 'source_uk', 'extra_uk',
            'image',
            'created', 'updated'
            ]

@admin.register(Term)                                                         # Regista o modelo Term na interface de administração do Django, permitindo a sua gestão através do painel de administração.
class TermAdmin(VersionAdmin, TranslationAdmin, ImportExportModelAdmin, ExportActionMixin):         # Classe TermAdmin herda de TranslationAdmin, permitindo que a interface de administração suporte a tradução dos campos do modelo Term.
    list_display = ['ref', 'id', 'name', 'area', 'subarea']                   # Define os campos do modelo que serão exibidos na lista de objetos na interface de administração.
    list_filter = ['subarea__area', 'subarea']                                # Adiciona filtros na interface de administração, permitindo filtrar os objetos com base na 'area' associada à 'subarea' ('subarea__area') e na 'subarea'
    search_fields = ['name']
    resource_classes = [TermResource]

    def area(self, obj):
        return obj.subarea.area
    area.short_description = 'Area'
    area.admin_order_field = 'subarea__area'

    # Ordenar as opções do ForeignKey 'subarea' no painel de administração
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'subarea':
            # Ordena as subáreas pela referência (ref) da subárea
            kwargs['queryset'] = SubArea.objects.all().order_by('ref')        # Ordena pelo campo 'ref' que já inclui ID da área
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(News)
class NewsAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_at', 'position', 'active',)
    list_filter = ('active',)
    list_editable = ('position', 'active',)
    search_fields = ('title', 'content')
    ordering = ('position', '-created_at',)


@admin.register(Warning)
class WarningAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('title', 'show_from', 'hide_after', 'created_at', 'position', 'active',)
    list_filter = ('active',)
    list_editable = ('position', 'active',)     # Editar a posição diretamente na lista
    search_fields = ('title', 'content')
    ordering = ('position', '-created_at',)


@admin.register(Tutorial)
class TutorialAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('title', 'position', 'active',)
    list_filter = ('active',)
    list_editable = ('position', 'active',)     # Editar a posição diretamente na lista
    search_fields = ('title', 'content')
    ordering = ('position',)                    # ordenar por posição no painel admin


@admin.register(Poster)
class PosterAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('title', 'position', 'active',)
    list_editable = ('position', 'active',)     # Editar a posição diretamente na lista
    ordering = ('position',)                    # ordenar por posição no painel admin

@admin.register(Thesis)
class ThesisAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('title', 'active',)

@admin.register(DocumentationLink)
class DocumentationLinkAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('name', 'url', 'position', 'active',)
    list_editable = ('position', 'active')
    search_fields = ('name', 'url',)

@admin.register(ContactInfo)
class ContactInfoAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('details', 'name', 'email', 'position', 'active')
    list_display_links = ('name',)
    list_editable = ('position', 'active')
    ordering = ('position',)


@admin.register(ContactTopMessage)
class ContactTopMessageAdmin(VersionAdmin, TranslationAdmin):
    list_display = ('text', 'show_from', 'hide_after', 'position', 'active',)
    list_editable = ('position', 'active',)

##############################################################################################
# Ação global: mover utilizadores do grupo 'SemAcesso' para 'Utilizador', sem ter que editar o UserAdmin
User = get_user_model()
def mover_para_utilizador(modeladmin, request, queryset):
    # Só faz sentido na lista de Users, daí a verificação com o "if"
    # Garante que só corre na lista de utilizadores
    if getattr(modeladmin, "model", None) is not User:
        messages.warning(request, "Esta ação só se aplica a utilizadores.")
        return

    try:
        sem_acesso = Group.objects.get(name="SemAcesso")
        utilizador = Group.objects.get(name="Utilizador")
    except Group.DoesNotExist as e:
        messages.error(request, f"Grupo em falta: {e}")
        return

    qs = queryset.prefetch_related("groups")
    movidos = 0
    with transaction.atomic():
        for user in qs:
            if sem_acesso in user.groups.all():
                user.groups.remove(sem_acesso)
                user.groups.add(utilizador)
                movidos += 1

    messages.success(
        request,
        f"{movidos} utilizador(es) movidos de 'SemAcesso' para 'Utilizador'."
    )

# Descrição no menu e permissões necessárias
mover_para_utilizador.short_description = "Mover de 'SemAcesso' para 'Utilizador'"
mover_para_utilizador.allowed_permissions = ('change',)
# Regista como ação global (fica disponível em todos os modelos, mas o próprio handler ignora se não for o User)
admin.site.add_action(mover_para_utilizador)
