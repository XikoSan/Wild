# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from storage.models.storage import Storage
from wild_politics.settings import JResponse
from django.utils.translation import ugettext
from django.utils.translation import pgettext


# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def start_auto(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if player.destination:
            data = {
                'response': pgettext('mining', 'Дождитесь конца полёта'),
                'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if player.premium < timezone.now():
            data = {
                'response': pgettext('mining', 'Премиум-аккаунт не активен. Продлите его'),
                'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        resource = request.POST.get('resource')

        if not resource in ['gold', 'oil', 'ore']:
            data = {
                'response': pgettext('mining', 'Неизвестный тип ресурса'),
                'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # если у игрока нет Склада в этом регионе, то Нефть и Руду собирать он не сможет
        if resource in ['ore', 'oil'] and not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                'response': pgettext('mining', 'У вас нет склада в этом регионе'),
                'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if AutoMining.objects.filter(player=player).exists():
            AutoMining.objects.filter(player=player).delete()

        AutoProduce = apps.get_model('factory.AutoProduce')
        if AutoProduce.objects.filter(player=player).exists():
            AutoProduce.objects.filter(player=player).delete()

        auto = AutoMining(
            player=player,
            resource=resource,
        )

        auto.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': ugettext('Ошибка метода'),

        }
        return JResponse(data)
