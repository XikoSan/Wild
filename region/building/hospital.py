# coding=utf-8
import math

from region.building.rate_building import RateBuilding


# госпиталь здание в регионе
class Hospital(RateBuilding):
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
        5: 16,
        4: 13,
        3: 12,
        2: 11,
        1: 9,
    }

    # получить строки с информацией об уровне и рейтинге здания
    @staticmethod
    def get_stat(region):

        if Hospital.objects.filter(region=region).exists():
            building = Hospital.objects.get(region=region)
            level = building.level
            top = building.top

        else:
            level = 0
            top = 1

        data = {
            'level': level,
            'top': top,
        }

        return data, 'region/buildings/hospital.html'

    # пересчитать рейтинг конкретных зданий
    @staticmethod
    def recount_rating():
        already_rated_pk = []
        kwargs = {}
        for i in Hospital.rating_percents.keys():
            if i == 5:
                kwargs['level__gt'] = 0
                top_5 = Hospital.objects.filter(**kwargs).order_by('-' + 'level').first()
                kwargs = {'top': 5}
                Hospital.objects.filter(pk=top_5.pk).update(**kwargs)
                already_rated_pk.append(top_5.pk)
            else:
                kwargs = {}
                if i != 1:
                    kwargs['level__gt'] = 0
                build_cnt = Hospital.objects.filter(**kwargs).exclude(pk__in=already_rated_pk).count()

                buildings = Hospital.objects.filter(**kwargs).exclude(pk__in=already_rated_pk).order_by(
                    '-' + 'level')[:math.ceil(build_cnt / 100 * Hospital.rating_percents.get(i))]

                for building in buildings:
                    kwargs = {'top': i}
                    Hospital.objects.filter(pk=building.pk).update(**kwargs)
                    already_rated_pk.append(building.pk)

    # Свойства класса
    class Meta:
        verbose_name = "Больница"
        verbose_name_plural = "Больницы"
