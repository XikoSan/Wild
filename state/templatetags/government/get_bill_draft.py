from django.template import Context, Library, loader
from django.http import HttpResponse
register = Library()


@register.simple_tag(takes_context=True)
def get_bill_draft(context):
    bill_cl = context['bill_cl']
    state = context['state']
    data, template = bill_cl.get_draft(state=state)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
