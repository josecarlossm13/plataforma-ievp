from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Divide uma string pelo separador especificado em 'arg'"""
    return value.split(arg)


# from django import template
#
# register = template.Library()
#
# @register.filter
# def getattribute(obj, attr):
#     """Retorna atributo dinâmico do objeto."""
#     return getattr(obj, attr, '')