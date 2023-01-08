from django import template

register = template.Library()

@register.filter(name='run_meth')
def run_meth(obj, fieldname):
    return getattr(obj, fieldname)()
