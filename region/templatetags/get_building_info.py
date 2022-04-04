from django.template import Context, Library, loader
from django.http import HttpResponse
register = Library()


@register.simple_tag(takes_context=True)
def get_building_info(context):
    building_cl = context['building_cl']
    region = context['region']
    data, template = building_cl.get_stat(region=region)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
