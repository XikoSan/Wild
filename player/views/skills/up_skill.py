import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.skill_training import SkillTraining
from player.player import Player
from wild_politics.settings import JResponse

# изучить навык
@login_required(login_url='/')
@check_player
@transaction.atomic
def up_skill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        skill = request.POST.get('skill')

        if skill not in ['power', 'knowledge', 'endurance']:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Нет такого навыка',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if player.cash < (getattr(player, skill) + 1) * 1000:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Недостаточно денег, необходимо: ' + str((getattr(player, skill) + 1) * 1000),
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': 'Навык уже изучается',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        player.cash -= (getattr(player, skill) + 1) * 1000

        new_skill = SkillTraining(
            player=player,
            skill=skill,
            end_dtime=timezone.now() + datetime.timedelta(hours=(getattr(player, skill) + 1)),
        )

        new_skill.save()
        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Изучение навыка',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
