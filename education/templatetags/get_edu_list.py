from django.template import Library, loader
from player.logs.skill_training import SkillTraining
register = Library()


@register.simple_tag(takes_context=True)
def get_edu_list(context, number):

    player = context['player']

    assistant_name = None
    if number == '1':
        assistant_name = context['assistant_name']

    full_queue = False
    if number == '9':
        skill_count = SkillTraining.objects.filter(player=player).count()
        if skill_count == 6:
            full_queue = True
            player.educated = True
            player.save()

    t = loader.get_template(f'education/edu_lists/list_{number}.html')
    return t.render({
        'full_queue': full_queue,
        'assistant_name': assistant_name,
        'player': player,
    })
