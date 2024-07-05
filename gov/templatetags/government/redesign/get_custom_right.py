from django.template import Context, Library, loader
from django.http import HttpResponse
register = Library()
from gov.models.custom_rights.custom_right import CustomRight


@register.simple_tag(takes_context=True)
def get_custom_right(context):
    class_name = context['class_name']
    state = context['state']

    right_cl = None

    custom_rights = CustomRight.__subclasses__()

    for c_right in custom_rights:

        if class_name == c_right.__name__:
            right_cl = c_right

    data, template = right_cl.get_new_form(state=state)

    if not template:
        data, template = right_cl.get_form(state=state)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
