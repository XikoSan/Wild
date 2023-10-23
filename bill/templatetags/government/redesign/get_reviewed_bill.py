from django.template import Library, loader

register = Library()


@register.simple_tag(takes_context=True)
def get_reviewed_bill(context):
    bill = context['bill']
    player = context['player']

    data, template = bill.get_new_reviewed_bill(player)

    if not template:
        data, template = bill.get_reviewed_bill(player)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
