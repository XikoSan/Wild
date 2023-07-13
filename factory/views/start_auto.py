# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from player.decorators.player import check_player
from factory.models.auto_produce import AutoProduce
from player.player import Player
from storage.models.storage import Storage
from wild_politics.settings import JResponse
from django.utils.translation import ugettext
from django.utils.translation import pgettext
from factory.models.project import Project


# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def start_auto_produce(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if player.destination:
            data = {
                'response': pgettext('mining', 'Дождитесь конца полёта'),
                'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        if player.premium < timezone.now():
            data = {
                'response': pgettext('mining', 'Премиум-аккаунт не активен. Продлите его'),
                'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        good = request.POST.get('good')
        produced_goods = []
        # собираем из Склада все поля ресурсов
        for category in ['materials', 'equipments', 'units']:
            for product in getattr(Storage, category).keys():
                if product == 'station':
                    continue
                produced_goods.append(product)

        if not good in produced_goods:
            data = {
                'response': pgettext('auto_produce', 'Неизвестный тип товара'),
                'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        # производится ли такой товар?
        if not getattr(Project, good):
            data = {
                'response': pgettext('auto_produce', 'Данный товар невозможно произвести'),
                'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        # проверка, существует ли у товара схема с таким номером
        schema_num = request.POST.get('schema')

        if not schema_num or \
                not schema_num.isdigit():
            data = {
                'response': pgettext('factory', 'Номер схемы - не число'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        schema_num = int(schema_num)

        if not (0 < schema_num <= len(getattr(Project, good)['resources'])):
            data = {
                'response': pgettext('factory', 'Указанной схемы не существует'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        storage_pk = request.POST.get('storage')

        # если у игрока нет Склада в этом регионе, то Нефть и Руду собирать он не сможет
        if not Storage.actual.filter(pk=storage_pk, owner=player).exists():
            data = {
                'response': pgettext('auto_produce', 'Указанный склад вам не принадлежит'),
                'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        if AutoProduce.objects.filter(player=player).exists():
            AutoProduce.objects.filter(player=player).delete()

        AutoMining = apps.get_model('player.AutoMining')
        if AutoMining.objects.filter(player=player).exists():
            AutoMining.objects.filter(player=player).delete()

        auto = AutoProduce(
            player=player,
            storage=Storage.actual.get(pk=storage_pk),
            good=good,
            schema=schema_num,
        )

        auto.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': pgettext('auto_produce', 'Ошибка автоматического производства'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': ugettext('Ошибка метода'),

        }
        return JResponse(data)
