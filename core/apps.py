# core/apps.py
from django.apps import AppConfig                           # Importa a classe AppConfig do Django, usada para configurar uma aplicação Django.

class CoreConfig(AppConfig):                                # Classe CoreConfig herda de AppConfig, permitindo configurar a aplicação 'core'.
    default_auto_field = 'django.db.models.BigAutoField'    # Define o tipo de campo automático padrão para os modelos como BigAutoField. Nºs inteiros grandes, o valor do campo é gerado automaticamente pela base de dados, começando em 1 e incrementando a cada novo registro.
    name = 'core'                                           # Define o nome da aplicação como 'core'.
