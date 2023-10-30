from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.logs.skill_training import SkillTraining
from player.player import Player
from player.views.get_subclasses import get_subclasses
from skill.models.skill import Skill


@login_required(login_url='/')
@check_player
def skills_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    names_dict = {}
    skills_dict = {}
    queue_dict = {}
    has_slot = True

    skills_count = SkillTraining.objects.filter(player=player).count() - 1

    if skills_count >= 5:
        has_slot = False

    # все виды навыков
    skills_classes = get_subclasses(Skill)

    for skill_cl in skills_classes:
        names_dict[skill_cl.__name__] = skill_cl._meta.verbose_name_raw

        has_right = skill_cl.check_has_right(player)

        # считаем, сколько у нас изучается навыков с этим именем
        skill_cnt = SkillTraining.objects.filter(player=player, skill=skill_cl.__name__).count()
        queue_dict[skill_cl.__name__] = skill_cnt

        # если навык уже изучен хоть сколько-то
        if skill_cl.objects.filter(player=player, level__gt=0).exists():
            skills_dict[skill_cl.__name__] = skill_cl.objects.get(player=player).level
        # если есть право изучать навык
        elif has_right:
            skills_dict[skill_cl.__name__] = 0

    train = SkillTraining.objects.filter(player=player).exists()

    premium = False

    if player.premium > timezone.now():
        premium = True

    attrs = ['power', 'knowledge', 'endurance']

    # отправляем в форму
    return render(request, 'redesign/skill/skill_list.html', {
        'page_name': _('Навыки'),

        'player': player,

        'skills_classes': skills_classes,
        'names_dict': names_dict,
        'skills_dict': skills_dict,
        'queue_dict': queue_dict,

        'premium': premium,
        'train': train,
        'has_slot': has_slot,

        'attrs': attrs,

    })
