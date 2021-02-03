from math import sin, cos, sqrt, atan2, radians

from region.views.distance_counting import distance_counting


# расстояние между регионами
# source, dest - инстанции класса Region
def time_in_flight(player, dest):
    # время в полёте при скорости 120 км/ч
    return (distance_counting(player.region, dest) / 120) * 60
