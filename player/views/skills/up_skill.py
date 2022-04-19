import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
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

        premium = False

        if player.premium > timezone.now():
            premium = True

        skill = request.POST.get('skill')

        if skill not in ['power', 'knowledge', 'endurance']:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Нет такого навыка',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # считаем, сколько у нас изучается навыков с этим именем
        skill_cnt = SkillTraining.objects.filter(player=player, skill=skill).count()

        if player.cash < (getattr(player, skill) + skill_cnt + 1) * 1000:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Недостаточно денег, необходимо: ' + str((getattr(player, skill) + skill_cnt + 1) * 1000),
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if not premium and SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': 'Навык уже изучается',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if SkillTraining.objects.filter(player=player).count() > 5:
            data = {
                'response': 'Очередь навыков заполнена',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        player.cash -= (getattr(player, skill) + skill_cnt + 1) * 1000

        cash_log = CashLog(player=player, cash=0 - (getattr(player, skill) + skill_cnt + 1) * 1000,
                           activity_txt='skill')
        cash_log.save()

        # время изучения навыка без према
        time_delta = datetime.timedelta(hours=(getattr(player, skill) + skill_cnt + 1))
        # с премом
        if player.premium > timezone.now():
            time_delta = datetime.timedelta(seconds=(getattr(player, skill) + skill_cnt + 1) * 2400)

        start = timezone.now()
        if SkillTraining.objects.filter(player=player).exists():
            # если есть навыки в очереди, берем время завершения от последнего
            start = SkillTraining.objects.filter(player=player).order_by('end_dtime').last().end_dtime

        new_skill = SkillTraining(
            player=player,
            skill=skill,
            end_dtime=start + time_delta,
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
