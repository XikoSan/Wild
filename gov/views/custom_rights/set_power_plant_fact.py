import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from region.building.power_plant import PowerPlant
from gov.models.minister_right import MinisterRight


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_power_plant_fact(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        points = 0

        right_cl_dict = {}

        plants = json.loads(request.POST.get('plants'))

        # игрок - министр
        if not Minister.objects.filter(player=player, state=player.region.state).exists():
            data = {
                'header': 'Министр энергетики',
                'grey_btn': 'Закрыть',
                'response': 'Вы не министр в государстве пребывания',
            }
            return JsonResponse(data)

        has_right = False
        # если у него есть соотв. права
        for right in Minister.objects.get(player=player, state=player.region.state).rights.all():
            if right.right == 'EnergyRights':
                has_right = True
                break

        if not has_right:
            data = {
                'header': 'Министр энергетики',
                'grey_btn': 'Закрыть',
                'response': 'Вы не министр энергетики',
            }
            return JsonResponse(data)

        for region_pk in plants.keys():
            # регион вообще существует
            if not Region.objects.filter(pk=region_pk, state=player.region.state).exists():
                data = {
                    'header': 'Министр энергетики',
                    'grey_btn': 'Закрыть',
                    'response': 'Региона с id ' + region_pk + ' в вашем государстве нет',
                }
                return JsonResponse(data)

            region = Region.objects.get(pk=region_pk)

            # если в регионе есть ТЭЦ
            if not PowerPlant.objects.filter(region=region).exists():
                data = {
                    'header': 'Министр энергетики',
                    'grey_btn': 'Закрыть',
                    'response': 'В регионе ' + region.region_name + ' нет ТЭЦ',
                }
                return JsonResponse(data)

            plant = PowerPlant.objects.get(region=region)

            try:
                fact_lvl = int(plants[region_pk])

            except ValueError:
                data = {
                    'header': 'Министр энергетики',
                    'grey_btn': 'Закрыть',
                    'response': 'Новый уровень ТЭЦ должен быть числом',
                }
                return JsonResponse(data)

            # если уровень ТЭЦ больше или равен используемому
            if plant.level < fact_lvl:
                data = {
                    'header': 'Министр энергетики',
                    'grey_btn': 'Закрыть',
                    'response': 'В регионе ' + region.region_name + ' уровень ТЭЦ ниже указанного',
                }
                return JsonResponse(data)

        for region_pk in plants.keys():
            if plant.level == int(plants[region_pk]):
                plant.level_on = None
            else:
                plant.level_on = plants[region_pk]
            plant.save()

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
