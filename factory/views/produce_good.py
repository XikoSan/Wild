import datetime
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import pgettext
from math import ceil
import redis
from factory.models.blueprint import Blueprint
from factory.models.component import Component
from factory.models.production_log import ProductionLog
from player.decorators.player import check_player
from player.player import Player
from storage.models.good import Good
from storage.models.stock import Stock
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_stocks
from storage.views.storage.locks.get_storage import get_storage


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
        try:
            good = int(request.POST.get('good'))

        except ValueError:
            return {
                'response': pgettext('factory', 'Указанный товар не существует'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }

        if not good or not Good.objects.filter(pk=good).exists():
            data = {
                'response': pgettext('factory', 'Указанный товар не существует'),
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
            }
            return JsonResponse(data)

        # lock_storage = get_storage(storage, [good, ])
        good = Good.objects.get(pk=good)
        goods = [good.name_ru, ]
        ret_stocks, ret_st_stocks = get_stocks(storage, goods)

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

        if not Blueprint.objects.filter(pk=schema_num).exists():
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
        sizetype_stocks = ret_st_stocks[good.size]
        if not storage.capacity_check(good.size, count, sizetype_stocks):
            data = {
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
                'response': pgettext('factory', 'Недостаточно места на складе для товара. В наличии ') + str(intcomma(
                    getattr(storage, good.size + '_cap') - sizetype_stocks)) + pgettext('factory',
                                                                                        ', требуется ') + str(
                    intcomma(count)),
            }
            return JsonResponse(data)

        # получить по номеру схемы схему
        schema = Blueprint.objects.get(pk=schema_num)

        # получить затраты энергии
        energy_cost = schema.energy_cost * count

        # только для материалов
        if good.type == 'materials':
            # если изучена Стандартизация
            Standardization = apps.get_model('skill.Standardization')
            if Standardization.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = Standardization.objects.get(player=player).level + 1
                # новая стоимость в энергии - цена за "пачку", даже неполную
                energy_cost = ceil(count / consignment) * schema.energy_cost

        # только для юнитов
        if good.type == 'units':
            # если изучено Режимное производство
            MilitaryProduction = apps.get_model('skill.MilitaryProduction')
            if MilitaryProduction.objects.filter(player=player, level__gt=0).exists():
                # лимит производства на единицу энергии
                consignment = MilitaryProduction.objects.get(player=player).level + 1
                # новая стоимость в энергии - цена за "пачку", даже неполную
                energy_cost = ceil(count / consignment) * schema.energy_cost

        # посчитать, хватает ли энергии для производства
        if energy_cost > player.energy \
                or energy_cost > 100:
            data = {
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
                'response': pgettext('factory', 'Недостаточно энергии. В наличии ') + str(player.energy) + pgettext(
                    'factory', ', требуется ') + str(
                    intcomma(energy_cost)),
            }
            return JsonResponse(data)

        # получить словарик со всеми читабальными названиями товаров
        goods_names = {
            'cash': pgettext('goods', 'Наличные'),
        }

        components = Component.objects.filter(blueprint=schema)

        # список с сырьём и продукцией
        goods = [good,]

        for component in components:
            # узнаем имя
            goods_names[component.good.pk] = component.good.name
            # добавляем сырье в список товаров, которые обрабатываются
            goods.append(component.good)

        # отдельная проверка на достаточность денег
        if schema.cash_cost * count > storage.cash:
            required = schema.cash_cost * count
            data = {
                'header': pgettext('factory', 'Ошибка производства'),
                'grey_btn': pgettext('storage', 'Закрыть'),
                'response': pgettext('factory', 'Недостаточно ') + str(goods_names['cash']) + pgettext('factory',
                                                                                                         '. В наличии ') + str(
                    intcomma(storage.cash)) + pgettext('factory', ', требуется ') + str(
                    intcomma(required)),
            }
            return JsonResponse(data)

        stocks = Stock.objects.select_for_update().filter(storage=storage, good__in=goods, stock__gt=0)

        # для каждого сырья в схеме производства
        for component in components:
            # узнать, хватает ли запасов на выбранном складе
            if not stocks.filter(good=component.good).exists() \
                    or component.count * count > stocks.get(good=component.good).stock:

                required = component.count * count
                if not stocks.filter(good=component.good).exists():
                    in_stock = 0
                else:
                    in_stock = stocks.get(good=component.good).stock

                data = {
                    'header': pgettext('factory', 'Ошибка производства'),
                    'grey_btn': pgettext('storage', 'Закрыть'),
                    'response': pgettext('factory', 'Недостаточно ') + str(goods_names[component.good.pk]) + pgettext('factory',
                                                                                                             '. В наличии ') + str(
                        intcomma(in_stock)) + pgettext('factory', ', требуется ') + str(
                        intcomma(required)),
                }
                return JsonResponse(data)

        # списать энергию игрока
        # player.energy_cons(value=energy_cost)
        player.energy_cons(value=energy_cost, mul=2)

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

        # списываем деньги отдельно
        storage.cash -= schema.cash_cost * count
        # создаём лог производства
        ProductionLog.objects.create(player=player,
                                     prod_storage=storage,
                                     good_move='outcm',
                                     cash=True,
                                     prod_value=schema.cash_cost * count,
                                     )

        # для каждого сырья в схеме
        for component in components:
            # установить новое значение Запаса
            stock = stocks.get(good=component.good)
            stock.stock -= component.count * count
            stock.save()
            # залогировать траты со склада
            # создаём лог производства
            ProductionLog.objects.create(player=player,
                                         prod_storage=storage,
                                         good_move='outcm',
                                         good=component.good,
                                         prod_value=component.count * count,
                                         )

        # добавить товар на склад
        stock, created = Stock.objects.get_or_create(
            storage=storage,
            good=good,
        )
        stock.stock += count
        stock.save()

        # сохранить склад
        storage.save()

        # удаляем записи старше месяца
        ProductionLog.objects.filter(player=player, dtime__lt=timezone.now() - datetime.timedelta(days=30)).delete()

        if player.party:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            # партийная информация
            if r.exists("party_factory_" + str(player.party.pk)):
                r.set("party_factory_" + str(player.party.pk),
                      int(float(r.get("party_factory_" + str(player.party.pk)))) + count)
            else:
                r.set("party_factory_" + str(player.party.pk), count)
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
