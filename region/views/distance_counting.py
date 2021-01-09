from math import sin, cos, sqrt, atan2, radians


# расстояние между регионами
# source, dest - инстанции класса Region
def distance_counting(source, dest):
    # радиус земли
    R = 6373.0
    # широта 1
    lat1 = radians(source.north)
    # долгота 1
    lon1 = radians(source.east)

    # если регионы находятся в одном полушарии по широте
    if source.is_north == dest.is_north:
        # широта 2
        lat2 = radians(dest.north)
    # регион прибытия в другом полушарии по широте
    else:
        # широта 2
        lat2 = 0 - radians(dest.north)

    # если регионы находятся в одном полушарии по широте
    if source.is_east == dest.is_east:
        # широта 2
        lon2 = radians(dest.east)
    else:
        # регион прибытия в другом полушарии по широте
        # широта 2
        lon2 = 0 - radians(dest.east)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # расстояние между регионами
    return R * c
