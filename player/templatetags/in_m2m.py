from django import template

register = template.Library()

@register.filter(name='in_m2m')
def in_m2m(instance, queryset):
    return queryset.filter(id=instance.id).exists()
