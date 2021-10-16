from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.factory.project import Project
from storage.views.storage.locks.get_storage import get_storage
from django.contrib.humanize.templatetags.humanize import intcomma
from storage.models.factory.production_log import ProductionLog


@login_required(login_url='/')
@check_player
@transaction.atomic
# новое торговое предложение
def produce_good(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        # получаем целевой склад
        source_pk = request.POST.get('storage')

        if not source_pk.isdigit():
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Склад не заполнен',
            }
            return JsonResponse(data)

        # проверяем, есть ли целевой склад среди складов игрока
        storages = Storage.actual.filter(owner=player).only('pk')

        storages_pk = []

        for storage in storages:
            storages_pk.append(storage.pk)

        if not int(source_pk) in storages_pk:
            data = {
                'header': 'Ошибка производства',
                'response': 'Указанный Склад вам не принадлежит',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        storage = Storage.actual.select_for_update().get(pk=int(source_pk))

        # проверка, существует ли такой ресурс вообще
        good = request.POST.get('good')
        if not hasattr(Storage, good):
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Указанный товар не существует',
            }
            return JsonResponse(data)

        lock_storage = get_storage(storage, [good, ])

        # проверка, существует ли у товара схема с таким номером
        schema_num = request.POST.get('schema')

        if not schema_num or\
                not schema_num.isdigit():
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Номер схемы - не число',
            }
            return JsonResponse(data)

        schema_num = int(schema_num)

        if not (0 < schema_num <= len(getattr(Project, good)['resources'])):
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Указанной схемы не существует',
            }
            return JsonResponse(data)

        # проверить, что количество товара в пределах Integer 0 < X < 2147483647
        count = request.POST.get('count')

        if not count.isdigit():
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Количество - не число',
            }
            return JsonResponse(data)

        count = int(count)

        if count <= 0:
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Количество товара должно быть положительным числом',
            }
            return JsonResponse(data)

        if count > 2147483647:
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Количество товара слишком велико',
            }
            return JsonResponse(data)

        # узнать, хватает ли места на складе для нового товара
        if count + getattr(lock_storage, good) > getattr(lock_storage, good + '_cap'):
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Недостаточно места на складе для товара. В наличии ' + str(intcomma(getattr(lock_storage, good + '_cap') - getattr(lock_storage, good))) + ', требуется ' + str(intcomma(count)),
            }
            return JsonResponse(data)

        # получить по номеру схемы схему
        schema = getattr(Project, good)['resources'][schema_num - 1]
        # получить затраты энергии
        energy_cost = getattr(Project, good)['energy'] * count
        # посчитать, хватает ли энергии для производства
        if energy_cost > player.energy \
                or energy_cost > 100:
            data = {
                'header': 'Ошибка производства',
                'grey_btn': 'Закрыть',
                'response': 'Недостаточно энергии. В наличии ' + str(player.energy) + ', требуется ' + str(intcomma(energy_cost)),
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
                    'header': 'Ошибка производства',
                    'grey_btn': 'Закрыть',
                    'response': 'Недостаточно ' + str(goods_names[material]) + '. В наличии ' + str(intcomma(getattr(storage, material))) + ', требуется ' + str(intcomma(required)),
                }
                return JsonResponse(data)

        # списать энергию игрока
        player.energy -= energy_cost
        # сохранить игрока
        player.save()
        # создаём лог производства
        production_log = ProductionLog(player=player, prod_storage=storage, prod_result=good)
        # для каждого сырья в схеме
        for material in schema.keys():
            # установить новое значени склада
            setattr(storage, material, getattr(storage, material) - (schema[material] * count))
            # залогировать траты со склада
            setattr(production_log, material, 0 - schema[material] * count)

        # добавить товар на склад
        setattr(storage, good, getattr(storage, good) + count)
        # залогировать приход на склад
        setattr(production_log, good, count)
        # сохранить склад
        storage.save()
        # сохранить лог
        production_log.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)
