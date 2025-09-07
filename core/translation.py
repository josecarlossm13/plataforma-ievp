# core/translation.py

from modeltranslation.translator import register, TranslationOptions    # Importa as funções e classes necessárias para registar modelos e definir opções de tradução.
from .models import Area, SubArea, Term, News, Warning, ContactTopMessage, \
    Tutorial, \
    Thesis, \
    DocumentationLink, \
    ContactInfo, \
    Poster  # Importa os modelos

# Utilização do django-modeltranslation, para adicionar suporte a traduções para o modelo "Area"
@register(Area)                                         # O decorador @register(Area) regista o modelo "Area" para que o django-modeltranslation saiba que ele deve ser tratado para traduções.
class AreaTranslationOptions(TranslationOptions):       # A classe AreaTranslationOptions herda de TranslationOptions e define quais campos do modelo devem ser traduzidos. Neste caso, especifiquei que o campo 'name' deve ser traduzido.
    fields = ['name']                                   # Especifica que o campo 'name' do modelo "Area" deve ser traduzido.
## Registro manual da classe AreaTranslationOptions. Sem o decorador @register teria de ser acrescentado explícitamente o seguinte:
# register(Area, AreaTranslationOptions)

# Utilização do django-modeltranslation, para adicionar suporte a traduções para o modelo "SubArea"
@register(SubArea)
class SubAreaTranslationOptions(TranslationOptions):
    fields = ['name']

# Utilização do django-modeltranslation, para adicionar suporte a traduções para o modelo "Term"
@register(Term)
class TermTranslationOptions(TranslationOptions):
    fields = ['name', 'description', 'source', 'extra', 'published_at']

@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ['title', 'content']

@register(Warning)
class WarningTranslationOptions(TranslationOptions):
    fields = ['title', 'content']

@register(Tutorial)
class TutorialTranslationOptions(TranslationOptions):
    fields = ['title', 'content', 'video_url']

@register(Poster)
class PosterTranslationOptions(TranslationOptions):
    fields = ['title', 'description', 'file']

@register(Thesis)
class ThesisTranslationOptions(TranslationOptions):
    fields = ['title', 'description']

@register(DocumentationLink)
class DocumentationLinkTranslationOptions(TranslationOptions):
    fields = ['name', 'url']

@register(ContactInfo)
class ContactInfoTranslationOptions(TranslationOptions):
    fields = ['details']

@register(ContactTopMessage)
class ContactTopMessageTranslationOptions(TranslationOptions):
    fields = ('text',)