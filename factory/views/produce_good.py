import datetime
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from math import ceil

from factory.models.production_log import ProductionLog
from factory.models.project import Project
from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_storage
from django.utils.translation import pgettext


@login_required(login_url='/')
@check_player
@transaction.atomic
# новое торговое предложение
def produce_good(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': pgettext('factory', 'Дождитесь конца полёта'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        # получаем целевой склад
        source_pk = request.POST.get('storage')

        if not source_pk.isdigit():
            data = {
                'response': pgettext('factory', 'Склад не заполнен'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.actual.filter(owner=player).only('pk')

        storages_pk = []

        for storage in storages:
            storages_pk.append(storage.pk)

        if not int(source_pk) in storages_pk:
            data = {
                'response': pgettext('factory', 'Указанный Склад вам не принадлежит'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        storage = Storage.actual.select_for_update().get(pk=int(source_pk))

        # проверка, существует ли такой ресурс вообще
        good = request.POST.get('good')
        if not good or not hasattr(Storage, good):
            data = {
                'response': pgettext('factory', 'Указанный товар не существует'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        lock_storage = get_storage(storage, [good, ])

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

        # проверить, что количество товара в пределах Integer 0 < X < 2147483647
        count = request.POST.get('count')

        if not count.isdigit():
            data = {
                'response': pgettext('factory', 'Количество - не число'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        count = int(count)

        if count <= 0:
            data = {
                'response': pgettext('factory', 'Количество товара должно быть положительным числом'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        if count > 2147483647:
            data = {
                'response': pgettext('factory', 'Количество товара слишком велико'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        # узнать, хватает ли места на складе для нового товара
        if count + getattr(lock_storage, good) > getattr(lock_storage, good + '_cap'):
            data = {
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
                'response': pgettext('factory', 'Недостаточно места на складе для товара. В наличии ') + str(intcomma(
                    getattr(lock_storage, good + '_cap') - getattr(lock_storage, good))) + pgettext('factory', ', требуется ') + str(
                    intcomma(count)),
            }
            return JsonResponse(data)

        # получить по номеру схемы схему
        schema = getattr(Project, good)['resources'][schema_num - 1]

        # получить затраты энергии
        energy_cost = getattr(Project, good)['energy'] * count

        # только для материалов
        if good in getattr(Storage, 'materials').keys():
            # если изучена Стандартизация
            Standardization = apps.get_model('skill.Standardization')
            if Standardization.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = Standardization.objects.get(player=player).level + 1
                # новая стоимость в энергии - цена за "пачку", даже неполную
                energy_cost = ceil(count / consignment) * getattr(Project, good)['energy']

        # только для юнитов
        if good in getattr(Storage, 'units').keys():
            # если изучено Режимное производство
            MilitaryProduction = apps.get_model('skill.MilitaryProduction')
            if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = MilitaryProduction.objects.get(player=player).level + 1
                # новая стоимость в энергии - цена за "пачку", даже неполную
                energy_cost = ceil(count / consignment) * getattr(Project, good)['energy']

        # посчитать, хватает ли энергии для производства
        if energy_cost > player.energy \
                or energy_cost > 100:
            data = {
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
                'response': pgettext('factory', 'Недостаточно энергии. В наличии ') + str(player.energy) + pgettext('factory', ', требуется ') + str(
                    intcomma(energy_cost)),
            }
            return JsonResponse(data)

        # получить словарик со всеми читабальными названиями товаров
        goods_names = {'cash': getattr(Storage, 'valut')['cash']}
        for db_type in getattr(Storage, 'types').keys():
            for good_db_name in getattr(Storage, db_type).keys():
                goods_names[good_db_name] = getattr(Storage, db_type)[good_db_name]

        # для каждого сырья в схеме производства
        for material in schema.keys():
            # узнать, хватает ли запасов на выбранном складе
            if schema[material] * count > getattr(storage, material):
                required = schema[material] * count
                data = {
                    'header': pgettext('factory', 'Ошибка производства'),
                    'grey_btn': pgettext('storage', 'Закрыть'),
                    'response': pgettext('factory', 'Недостаточно ') + str(goods_names[material]) + pgettext('factory', '. В наличии ') + str(
                        intcomma(getattr(storage, material))) + pgettext('factory', ', требуется ') + str(intcomma(required)),
                }
                return JsonResponse(data)

        # списать энергию игрока
        player.energy_cons(energy_cost)

        # from player.game_event.energy_spent import EnergySpent
        # from django.contrib.humanize.templatetags.humanize import number_format
        # sum = None
        #
        # if EnergySpent.objects.filter(player=player).exists():
        #     e_spent = EnergySpent.objects.get(player=player)
        #     e_spent.points += energy_cost
        #     sum = e_spent.claim_reward()
        #
        # else:
        #     e_spent = EnergySpent(player=player, points=energy_cost)
        #     e_spent.save()

        # создаём лог производства
        ProductionLog.objects.create(player=player,
                                     prod_storage=storage,
                                     good_move='incom',
                                     good=good,
                                     prod_value=count,
                                     )
        # для каждого сырья в схеме
        for material in schema.keys():
            # установить новое значени склада
            setattr(storage, material, getattr(storage, material) - (schema[material] * count))
            # залогировать траты со склада
            # создаём лог производства
            ProductionLog.objects.create(player=player,
                                         prod_storage=storage,
                                         good_move='outcm',
                                         good=material,
                                         prod_value=schema[material] * count,
                                         )

        # добавить товар на склад
        setattr(storage, good, getattr(storage, good) + count)
        # сохранить склад
        storage.save()

        # удаляем записи старше месяца
        ProductionLog.objects.filter(player=player, dtime__lt=timezone.now() - datetime.timedelta(days=30)).delete()

        # if sum:
        #     data = {
        #         'header': pgettext('factory', 'Внезапно!'),
        #         'grey_btn': pgettext('factory', 'Отлично!'),
        #         'response': pgettext('factory', 'Вы получили ') + number_format(sum) + pgettext('factory', ' золота'),
        #     }
        #     return JsonResponse(data)

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)
