# coding=utf-8
import math

from region.building.rate_building import RateBuilding
from region.building.power_plant import PowerPlant
from state.models.state import State
from django.utils.translation import pgettext_lazy


# инфраструктура здание в регионе
class Infrastructure(RateBuilding):
    # словарь индексов, с процентом от числа зданий (за вычетом вышест. рейтингов)
    rating_percents = {
        5: 1,
        4: 10,
        3: 20,
        2: 30,
        1: 100,
    }

    # словарь индексов конкретного здания, с соотв. эффектом
    indexes = {
        5: 50,
        4: 25,
        3: 20,
        2: 15,
        1: 0,
    }

    # потребление электричества, уровень
    power_consumption = 2

    # получить строки с информацией об уровне и рейтинге здания
    @staticmethod
    def get_stat(region):

        if Infrastructure.objects.filter(region=region).exists():
            building = Infrastructure.objects.get(region=region)
            level = building.level
            # top = building.get_top()
            top = building.top

        else:
            level = 0
            top = 1

        data = {
            'level': level,
            'top': top,
        }

        return data, 'region/redesign/buildings/infrastructure.html'

    # пересчитать рейтинг конкретных зданий
    @staticmethod
    def recount_rating():
        already_rated_pk = []
        kwargs = {}

        efficiency_dict = {}
        real_level = ()

        # для каждого здания считаем его уровень, с поправкой на электросеть
        for building in Infrastructure.objects.all():

            if building.region.state:
                # если для этого госа уже знаем эффективность
                if building.region.state in efficiency_dict:
                    efficiency = efficiency_dict[building.region.state]

                else:
                    efficiency = PowerPlant.get_power_efficiency(state=building.region.state)
                    efficiency_dict[building.region.state] = efficiency

            else:
                efficiency = PowerPlant.get_power_efficiency(region=building.region)

            # список с госпиталями и реальным уровнем. Словарь здесь не подойдет, нужно сортировать
            real_level += ((building, math.floor(building.level * (efficiency / 100))), )

        real_level = sorted(real_level, key=lambda x: x[1], reverse=True)

        for i in Infrastructure.rating_percents.keys():
            if i == 5:
                if real_level[0][1] == 0:
                    continue

                top_5 = real_level.pop(0)[0]
                kwargs = {'top': 5}
                Infrastructure.objects.filter(pk=top_5.pk).update(**kwargs)
                already_rated_pk.append(top_5.pk)

            else:
                # количество зданий в списке с факт уровенм больше нуля
                build_cnt = 0
                for build in real_level:
                    if i != 1 and build[1] == 0:
                        break
                    build_cnt += 1

                # берем только здания ненулевого уровня
                buildings = real_level[:build_cnt]

                # берем процент от этих зданий, которые и получат рейтинг
                buildings = buildings[:math.ceil(build_cnt / 100 * Infrastructure.rating_percents.get(i))]

                real_level = real_level[len(buildings):]

                # список айди госпиталей, которые обновляем
                hosp_pk_list = []
                for hosp in buildings:
                    hosp_pk_list.append(hosp[0].pk)

                Infrastructure.objects.filter(pk__in=hosp_pk_list).update(top=i)

    # Свойства класса
    class Meta:
        verbose_name = pgettext_lazy('new_bill', "Инфраструктура")
        verbose_name_plural = pgettext_lazy('new_bill', "Инфраструктуры")
