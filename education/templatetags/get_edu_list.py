from django.template import Library, loader

register = Library()


@register.simple_tag(takes_context=True)
def get_edu_list(context, number):

    player = context['player']

    assistant_name = None
    if number == '1':
        assistant_name = context['assistant_name']

    t = loader.get_template(f'education/edu_lists/list_{number}.html')
    return t.render({
        'assistant_name': assistant_name,
        'player': player,
    })
