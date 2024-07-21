import heapq
import math
import redis
import json
from django.db.models import Q

from region.models.neighbours import Neighbours
from region.models.region import Region


# Функция для сохранения словаря в Redis
def save_dict_to_redis(redis_client, key, data):
    # Сериализуем словарь в строку JSON
    json_data = json.dumps(data)
    # Сохраняем строку в Redis по заданному ключу
    redis_client.set(key, json_data)


# Функция для загрузки словаря из Redis
def load_dict_from_redis(redis_client, key):
    # Получаем строку из Redis по ключу
    json_data = redis_client.get(key)
    if json_data is None:
        return None
    # Десериализуем строку обратно в словарь
    return json.loads(json_data)


def find_route(start_region, end_region, excluded_regions=None, price=1, force_recount=False):

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    # Проверяем наличие исключенных регионов
    if excluded_regions is None:
        excluded_regions = []

    # Получаем IDs исключенных регионов для быстрого доступа
    excluded_region_ids = {region.id for region in excluded_regions}

    # Загружаем все регионы из базы данных и создаем словарь regions
    regions = {region.id: region for region in Region.objects.all() if region.id not in excluded_region_ids}

    if not force_recount:

        if r.exists(f'route_price_{start_region.id}__{end_region.id}'):

            from player.logs.print_log import log
            log(' - - - ')

            path = load_dict_from_redis(r, f'route_{start_region.id}__{end_region.id}')
            route = [regions[region_id] for region_id in path]

            price = int(r.get(f'route_price_{start_region.id}__{end_region.id}'))

            log(f'{start_region.id} _ {end_region.id} _ price: {price}')

            return route,price

        else:
            return find_route(start_region, end_region, excluded_regions, price, force_recount=True)


    else:
        # Загружаем все соседства из базы данных
        neighbours = Neighbours.objects.all()

        # Создаем список смежности (adjacency list) и заранее вычисляем расстояния между соседними регионами
        adjacency_list = {region_id: [] for region_id in regions.keys()}
        distances = {}

        for neighbour in neighbours:
            region_1_id = neighbour.region_1_id
            region_2_id = neighbour.region_2_id

            # Пропускаем связи, если один из регионов находится в списке исключенных
            if region_1_id in excluded_region_ids or region_2_id in excluded_region_ids:
                continue

            distance = regions[region_1_id].distance_to(regions[region_2_id])

            # Добавляем соседей в список смежности и сохраняем расстояния между ними
            adjacency_list[region_1_id].append((region_2_id, distance))
            adjacency_list[region_2_id].append((region_1_id, distance))
            distances[(region_1_id, region_2_id)] = distance
            distances[(region_2_id, region_1_id)] = distance

        # Алгоритм Дейкстры
        queue = [(0, start_region.id, [])]  # Очередь с приоритетом, начинаем с начального региона
        seen = set()  # Множество посещенных регионов
        distances_from_start = {start_region.id: 0}  # Расстояния от начального региона до всех остальных

        while queue:
            # Извлекаем регион с наименьшей стоимостью из очереди
            (cost, current_region_id, path) = heapq.heappop(queue)

            if current_region_id in seen:
                continue

            seen.add(current_region_id)  # Помечаем регион как посещенный
            path = path + [current_region_id]  # Добавляем текущий регион в путь

            if current_region_id == end_region.id:
                # Если достигли конечного региона, возвращаем путь и его общую длину
                total_distance = cost

                save_dict_to_redis(r, f'route_{start_region.id}__{end_region.id}', path)
                r.set(f'route_price_{start_region.id}__{end_region.id}', total_distance)

                return [regions[region_id] for region_id in path], total_distance

            # Проходимся по всем соседям текущего региона
            for next_region_id, distance in adjacency_list[current_region_id]:
                if next_region_id in seen:
                    continue

                cost_per_100km = math.ceil(distance / 100) * price

                new_cost = cost + cost_per_100km  # Вычисляем новую стоимость до соседнего региона

                if new_cost < distances_from_start.get(next_region_id, float('inf')):
                    # Если найден более короткий путь до соседнего региона, обновляем стоимость и добавляем в очередь
                    distances_from_start[next_region_id] = new_cost
                    heapq.heappush(queue, (new_cost, next_region_id, path))


        # save_dict_to_redis(r, f'route_{start_region.id}__{end_region.id}', [])
        # r.set(f'route_price_{start_region.id}__{end_region.id}', 30)

        return [], 30  # Если путь не найден, возвращаем пустой список и нулевое расстояние
