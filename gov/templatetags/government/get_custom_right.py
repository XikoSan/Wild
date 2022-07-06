from django.template import Context, Library, loader
from django.http import HttpResponse
register = Library()


@register.simple_tag(takes_context=True)
def get_custom_right(context):
    right_cl = context['right_cl']
    state = context['state']
    data, template = right_cl.get_form(state=state)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
