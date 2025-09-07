# core/models.py
from ckeditor_uploader.fields import RichTextUploadingField     # Para fazer edição de texto rico e upload de imagens no CKEditor.
from django.db import models                                    # Importa o módulo models do Django, que contém classes para definir modelos de dados.
from django.utils.translation import gettext_lazy as _          # Importa a função gettext lazy do Django, renomeando-a como '_', para facilitar a tradução de strings.
import reversion
from django.utils import timezone
from modeltranslation.utils import build_localized_fieldname
from django.conf import settings


# Modelo para a área de conhecimento
@reversion.register()
class Area(models.Model):                                                                       # Classe Area herda de models.Model, representando um modelo de dados no Django.
    id = models.CharField(_('Id'), max_length=3, primary_key=True)                              # Define o campo 'id' como um IntegerField, que é a chave primária do modelo. Cada 'id' é único.
    name = models.CharField(_('Name'), max_length=255, unique=True, null=True, blank=True)      # Define o campo 'name' como um CharField, com um nome traduzido e restrição de ser único.

    class Meta:                                         # Classe interna Meta para definir opções adicionais do modelo.
        verbose_name = _('Area')                        # verbose_name é uma string que fornece um nome legível para o modelo, por ex. no painel de administração do django
    def __str__(self):                                  # Metodo que define a representação em string do modelo.
        return f"{self.id} {self.name}"                 # Retorna uma string formatada com o 'id' e o 'name' da área.


# Modelo para a subárea de conhecimento
@reversion.register()
class SubArea(models.Model):
    ref = models.CharField(_('Reference'), max_length=6, editable=False, primary_key=True) # Ex: 301-01
    id = models.CharField(_('Id'), max_length=2) # Ex: 01
    name = models.CharField(_('Name'), max_length=255, null=True, blank=True)       # Define o campo 'name' como um CharField, com um nome traduzido e restrição de ser único.
    area = models.ForeignKey(Area, verbose_name=_('Area'), related_name='subareas', on_delete=models.PROTECT)       # Define uma ForeignKey que faz referência ao modelo Area, permitindo associar uma SubArea a uma Area.

    class Meta:                                         # Classe interna Meta para definir opções adicionais do modelo.
        verbose_name = _('Subarea')                     # verbose_name é uma string que fornece um nome legível para o modelo, por ex. no painel de administração do django

    def save(self, *args, **kwargs):
        # Formata o ID com 2 dígitos, apenas se for numérico
        if self.id and self.id.isdigit():
            self.id = f"{int(self.id):02d}"

        self.ref = f"{self.area.id}-{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):                                   # Metodo que define a representação em string do modelo.
        return f"{self.ref} {self.name}"                 # Retorna uma string formatada com o 'id' da área, o 'id' da subárea (com pelo menos dois dígitos inteiros) e o 'name' da subárea.


# Modelo para os termos/vocábulos
@reversion.register()
class Term(models.Model):                               # Classe Term herda de models.Model, representando um modelo de dados no Django.
    ref = models.CharField(_('IEV Reference'), max_length=9, editable=False, primary_key=True)  # Ex: 301-01-01
    id = models.CharField(_('Id'), max_length=2)        # Ex: 01
    subarea = models.ForeignKey(SubArea, verbose_name=_('Subarea'), related_name='termos', on_delete=models.PROTECT)    # Define uma ForeignKey que faz referência ao modelo SubArea, permitindo associar um Term a uma SubArea.
    name = models.CharField(_('Name'),max_length=255, null=True, blank=True)    # Define o campo 'name' como um CharField, com um nome traduzido e restrição de ser único.
    description = RichTextUploadingField(_('Description'), null=True)   # Define o campo 'description' como um RichTextUploadingField, para descrever o termo, com formatações e possibilidade de imagens, usando o CKeditor.
    source = models.TextField(_('Source'), blank=True, null=True)   # Define o campo 'source' como um TextField, que pode ser deixado em branco ou nulo, para indicar a fonte do termo.
    image = models.ImageField(_('Image'), upload_to='imagens/', null=True, blank=True)  # Define o campo 'image' como um ImageField, que pode ser nulo ou em branco, para armazenar uma imagem associada ao termo.
    extra = RichTextUploadingField(blank=True, null=True)           # Define o campo 'extra' como um RichTextField, permitindo a edição de texto rico.

    created = models.DateTimeField(_('Created'), auto_now_add=True, null=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True, null=True)

    ####### Added to IEVP #### carimbo por idioma (o modeltranslation criará published_at_en, _pt, _es, …)
    published_at = models.DateTimeField(_('Added to IEVP'), null=True, blank=True)
    ######################################################################

    def save(self, *args, **kwargs):
        self.ref = f"{self.subarea.ref}-{self.id}"
        ############################## Added to IEVP ##############################
        # --- carimbar published_at_<lang> só na 1ª vez em que esse idioma ganha conteúdo ---
        now = timezone.now()
        bases = ['name', 'description', 'source', 'extra']

        old = None
        if self.pk:
            try:
                old = Term.objects.get(pk=self.pk)
            except Term.DoesNotExist:
                old = None

        for lang_code, _label in settings.LANGUAGES:
            pub_field = build_localized_fieldname('published_at', lang_code)

            # só se ainda não tem data para este idioma
            if getattr(self, pub_field, None) is None:
                # há conteúdo agora neste idioma?
                has_now = any(
                    bool((getattr(self, build_localized_fieldname(base, lang_code), None) or '').strip())
                    for base in bases
                )
                # havia conteúdo antes?
                had_before = any(
                    bool((getattr(old, build_localized_fieldname(base, lang_code), None) or '').strip())
                    for base in bases
                ) if old else False

                # define a data apenas quando passa de vazio -> com conteúdo
                if has_now and not had_before:
                    setattr(self, pub_field, now)
        ######################################################################
        super().save(*args, **kwargs)

    class Meta:                                         # Classe interna Meta para definir opções adicionais do modelo.
        verbose_name = _('Term')                        # verbose_name é uma string que fornece um nome legível para o modelo, por ex., no painel de administração do Django.

    def __str__(self):                                  # Metodo que define a representação em string do modelo.
        return f"{self.ref} {self.name}"                # Retorna uma string formatada com a referência IEV e o nome do termo.


# Para mostrar mensagens de notícias na homepage
class News(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    content = RichTextUploadingField(_('Content'))

    active = models.BooleanField(_('Active'), default=True)
    start_date = models.DateTimeField('Show from', null=True, blank=True)
    end_date = models.DateTimeField('Hide after', null=True, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    position = models.PositiveIntegerField('Position', default=0)

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ('position', '-created_at')

    def is_valid_now(self):
        now = timezone.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    def __str__(self):
        return f"{self.title} ({'Active' if self.active else 'Inactive'})"

# Para mostrar mensagens de avisos na homepage
class Warning(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = RichTextUploadingField(_('Content'))
    active = models.BooleanField(default=True, verbose_name='Active')
    show_from = models.DateTimeField(null=True, blank=True, verbose_name='Show from')
    hide_after = models.DateTimeField(null=True, blank=True, verbose_name='Hide after')
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField('Position', default=0)


    class Meta:
        verbose_name = _('Warning')
        verbose_name_plural = _('Warnings')
        ordering = ['position','-created_at']

    def __str__(self):
        return self.title


class Tutorial(models.Model):
    title = models.CharField(_('Title'), max_length=255 )
    content = RichTextUploadingField(_('Content'))                      # Texto que explica o tutorial
    video_url = models.URLField(_('Video URL'), blank=True, null=True)  # URL do vídeo tutorial

    restricted = models.BooleanField(default=False)                     # campo para selecionar se é restrito a staff
    active = models.BooleanField('Active', default=True)
    position = models.PositiveIntegerField('Position', default=0, blank=True, null=True)

    class Meta:
        verbose_name = _('Tutorial')
        verbose_name_plural = _('Tutorials')
        ordering = ['position']

    def __str__(self):
        return f"{self.title} ({'Active' if self.active else 'Inactive'})"


class Poster(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = RichTextUploadingField(verbose_name=_('Description'), blank=True, null=True)
    file = models.FileField(upload_to='poster/', verbose_name=_('PDF File'))
    active = models.BooleanField(default=True, verbose_name='Active')
    position = models.PositiveIntegerField('Position', default=0, blank=True, null=True)

    class Meta:
        verbose_name = _('Poster')
        verbose_name_plural = _('Posters')
        ordering = ['position']


    def __str__(self):
        return self.title


class Thesis(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = RichTextUploadingField(verbose_name=_('Description'), blank=True, null=True)
    file = models.FileField(upload_to='thesis/', verbose_name='PDF File')
    active = models.BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return self.title


class DocumentationLink(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Link Name'))
    url = models.URLField(verbose_name=_('URL'))
    active = models.BooleanField(default=True, verbose_name='Active')
    position = models.PositiveIntegerField('Position', default=0, blank=True, null=True)

    class Meta:
        ordering = ['position']



    def __str__(self):
        return self.name


class ContactInfo(models.Model):
    position = models.PositiveIntegerField('Position', default=0)
    details = models.CharField(_('Details'), max_length=255, blank=True, null=True)
    name = models.CharField('Name', max_length=255)
    email = models.EmailField('Email')
    active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ['position']
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return f"{self.name} ({self.email})"

# Publicar mensagens na página contacts
class ContactTopMessage(models.Model):
    text = models.TextField(_('Message'))
    active = models.BooleanField(default=True)
    show_from = models.DateTimeField(null=True, blank=True)
    hide_after = models.DateTimeField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('position', '-id')

    def __str__(self):
        return f"{self.position} – {self.text}"
