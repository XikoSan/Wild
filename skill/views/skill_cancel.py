import copy
import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.logs.skill_training import SkillTraining
from player.player import Player


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
                'response': _('ID навыка должен быть числом'),
                'header': _('Ошибка отмены навыка'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

        if not player.premium > timezone.now():
            data = {
                'response': _('У вас нет активного премиум-аккаунта'),
                'header': _('Ошибка отмены навыка'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

        if not SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': _('Нет навыков в очереди'),
                'header': _('Ошибка отмены навыка'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

        skills = SkillTraining.objects.filter(player=player)

        if skills.count() < 2:
            data = {
                'response': _('Нет навыков в очереди'),
                'header': _('Ошибка отмены навыка'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

        queue = copy.deepcopy(skills.order_by('end_dtime')[1:])

        last_skill = None
        # при попытке взять .last() ругается, херня какая-то
        for q in queue:
            last_skill = q

        if last_skill.pk != id:
            data = {
                'response': _('Нет такого навыка'),
                'header': _('Ошибка отмены навыка'),
                'grey_btn': _('Закрыть'),
            }
            return JsonResponse(data)

        if last_skill.skill in ('power', 'knowledge', 'endurance'):
            refund = (getattr(player, last_skill.skill) + SkillTraining.objects.filter(player=player,
                                                                                       skill=last_skill.skill).count()) * 1000
            player.cash += refund

        last_skill.delete()
        player.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
