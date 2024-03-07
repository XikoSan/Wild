from django.db.models import Q

from region.models.neighbours import Neighbours
from region.models.region import Region
from django.utils import timezone


# получить список целевых регионов
def get_victims(state):
    # словарь регион - соседние регионы
    victims_list = {}
    # лист соседних регоинов
    victims = []
    # регион для добавления в лист
    victim = None
    # список регион - связанные соседи
    neig_list = {}
    # список регионов
    regions = Region.objects.filter(state=state)
    # отбираем словарик регион - экземпляры Соседей
    for region in regions:
        # сохраняем только те, где эти экземпляры есть
        if Neighbours.objects.filter(Q(region_1=region) | Q(region_2=region)).exists():
            neig_list[region] = Neighbours.objects.filter(Q(region_1=region) | Q(region_2=region))
    # т.к. Соседи содержат два региона, отбираем из связей только второй
    for region in neig_list.keys():
        victims.clear()
        # по каждой связи находим связанный регион
        for neig in neig_list.get(region):
            # нам нужен не сам регион, а сосед
            if neig.region_1 == region:
                victim = neig.region_2
            else:
                victim = neig.region_1
            # если государство соседа отличается от исходного
            # и регион не выключен
            # и в нем истекло мирное время
            if victim.state != region.state and not victim.is_off and timezone.now() > victim.peace_date:
                victims.append(victim)
        # заполненный лист добавляем в словарь (если регион окружен своими же регионами, они не нужны)

        if victims:
            victims_list[region] = victims.copy()

    return victims_list
