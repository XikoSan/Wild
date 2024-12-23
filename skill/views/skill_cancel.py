import copy
import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import pgettext
from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.logs.skill_training import SkillTraining
from player.player import Player
from player.views.multiple_sum import multiple_sum



# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def skill_cancel(request):
    if request.method == "POST":

        # получаем персонажа
        player = Player.get_instance(account=request.user)

        id = None
        dest_pk = request.POST.get('skill')

        try:
            id = int(dest_pk)
        # нет такого опроса
        except ValueError:
            data = {
                'response': pgettext('skills', 'ID навыка должен быть числом'),
                'header': pgettext('skills', 'Отмена навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if not player.premium > timezone.now():
            data = {
                'response': pgettext('skills', 'У вас нет активного премиум-аккаунта'),
                'header': pgettext('skills', 'Отмена навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if not SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': pgettext('skills', 'Нет навыков в очереди'),
                'header': pgettext('skills', 'Отмена навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        skills = SkillTraining.objects.filter(player=player)

        if skills.count() < 2:
            data = {
                'response': pgettext('skills', 'Нет навыков в очереди'),
                'header': pgettext('skills', 'Отмена навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        queue = copy.deepcopy(skills.order_by('end_dtime')[1:])

        last_skill = None
        # при попытке взять .last() ругается, херня какая-то
        for q in queue:
            last_skill = q

        if last_skill.pk != id:
            data = {
                'response': pgettext('skills', 'Нет такого навыка'),
                'header': pgettext('skills', 'Отмена навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if last_skill.skill in ('power', 'knowledge', 'endurance'):
            refund = multiple_sum((
                             (getattr(player, last_skill.skill) + SkillTraining.objects.filter(player=player,
                                                                                               skill=last_skill.skill).count())
                             ** 2) * 10)
            player.cash += refund

        last_skill.delete()
        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('skills', 'Отмена навыка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
