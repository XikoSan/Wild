from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from wild_politics.settings import JResponse
from django.utils import timezone

# запуск войны в текущем регионе
@login_required(login_url='/')
@check_player
@transaction.atomic
def send_squads(request):
    # todo:
    # проверять, что склад совпадает с регионом атаки или защиты
    # сделать универсальную отправку, а не только автоматы
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        if not Storage.objects.filter(owner=player, region=player.region).exists():
            data = {
                'response': 'Нет Склада отправки войск в регионе',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        storage = Storage.objects.select_for_update().get(owner=player, region=player.region)

        # получаем войну
        try:
            war_pk = int(request.POST.get('war_id'))

        except ValueError:
            data = {
                'response': 'ID войны указан некорректно',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        try:
            war_class = apps.get_model('war', request.POST.get('war_type'))

        except KeyError:
            data = {
                'response': 'Такого вида войн нет',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if not war_class.objects.filter(pk=war_pk, deleted=False, running=True).exists():
            data = {
                'response': 'Нет такой войны',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if not request.POST.get('side') in ['agr', 'def']:
            data = {
                'response': 'Нет такой стороны боя',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        war = war_class.objects.get(pk=war_pk)

        squads_list = getattr(war, 'squads_list')

        energy_sum = 0

        # rifles: 25, Infantry, true - отряд для 25 автоматов уже есть,
        squads_count_class = {}

        # словарь: тип отряда - наличие
        squads_avail_dict = {}

        # признак того, что хотя бы один юнит указан (не нулевой)
        has_units = False

        for squad_type in squads_list:
            if not hasattr(war, squad_type):
                continue
            # для каждого юнита в каждом типе отрядов этой войны
            for unit in getattr(getattr(getattr(war, squad_type), 'model'), 'specs').keys():

                unit_class = getattr(getattr(war, squad_type), 'model')

                if request.POST.get(unit):

                    try:
                        unit_count = int(request.POST.get(unit))

                    except ValueError:
                        data = {
                            'response': 'Количество юнитов - не число',
                            'header': 'Отправка войск',
                            'grey_btn': 'Закрыть',
                        }
                        return JResponse(data)

                    if unit_count < 0:
                        data = {
                            'response': 'Допустимы только положительные значения',
                            'header': 'Отправка войск',
                            'grey_btn': 'Закрыть',
                        }
                        return JResponse(data)

                    if unit_count == 0:
                        continue

                    has_units = True

                    if getattr(storage, unit) < unit_count:
                        data = {
                            'response': 'Недостаточно войск (' + getattr(unit_class, 'specs')[unit]['name'] + ') на Складе',
                            'header': 'Отправка войск',
                            'grey_btn': 'Закрыть',
                        }
                        return JResponse(data)

                    energy_sum += getattr(unit_class, 'specs')[unit]['energy'] * unit_count

                    # проверяем, известно ли нам о наличии или отсутсвии отряда такого типа
                    if not unit_class in squads_avail_dict:
                        # узнаем, нужен ли новый объект для юнитов. Если нужен будет, сделаем
                        if unit_class.objects.filter(owner=player, object_id=war_pk, deleted=False,
                                                     side=request.POST.get('side')).exists():
                            squads_count_class[unit] = [unit_count, unit_class, True]
                            squads_avail_dict[unit_class] = True
                        else:
                            squads_count_class[unit] = [unit_count, unit_class, False]
                            squads_avail_dict[unit_class] = False

                    else:
                        squads_count_class[unit] = [unit_count, unit_class, squads_avail_dict[unit_class]]

        if not has_units:
            data = {
                'response': 'Не указан ни один юнит к отправке',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if energy_sum > player.energy:
            data = {
                'response': 'Недостаточно энергии',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        new_squads_dict = {}

        for unit in squads_count_class.keys():

            unit_list = squads_count_class[unit]

            squad = None
            # unit_list[2] - это наличие объекта отряда для юнита
            if unit_list[2]:
                # unit_list[1] - это класс юнита
                squad = unit_list[1].objects.select_for_update().get(owner=player, object_id=war_pk, deleted=False,
                                             side=request.POST.get('side'))

            else:
                if unit_list[1] in new_squads_dict:
                    squad = new_squads_dict[unit_list[1]]

                else:
                    # создаем новый отряд
                    squad = unit_list[1](
                        owner=player,
                        content_object=war,
                        side=request.POST.get('side'),
                        deploy=timezone.now()
                    )

                    new_squads_dict[unit_list[1]] = squad

            setattr(squad, unit, getattr(squad, unit) + unit_list[0])

            squad.save()

        player.energy -= energy_sum
        player.save()

        for unit in squads_count_class.keys():

            setattr(storage, unit, getattr(storage, unit) - squads_count_class[unit][0])

        storage.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Отправка войск',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
