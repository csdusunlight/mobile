from django import template
register = template.Library()
@register.filter('list')
def do_list(value):
    return range(1, value+1)

@register.filter('modulo')
def do_modulo(value, arg):
    return value%int(arg)