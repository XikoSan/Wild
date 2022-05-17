from django.template import Library, loader

register = Library()


@register.simple_tag(takes_context=True)
def get_bill(context):
    bill = context['bill']
    player = context['player']
    minister = context['minister']
    president = context['president']
    data, template = bill.get_bill(player, minister, president)

    t = loader.get_template(template)
    return t.render({
        'data': data,
    })
