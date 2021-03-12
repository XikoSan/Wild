from player.player import Player
from storage.models.storage import Storage


# проверка наличия товаров на указанных Складах, перед списанием их оттуда
# входные данные:
# storages - список всех складов, по котором надо проверять
# values   - формат данных JSON из запроса

# выходные данные:
# status   - всё ОК или нет
# storage  - Склад, на котором не хватило товара
# good     - имя товара, которого не хватает
# required - сколько запросили товара
# exist    - сколько было товара на складе в момент проверки
def check_goods_exists(storages, values):
    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идём по списку товаров
            for good in values.get(storage):
                # проверка, существует ли такой ресурс вообще
                if not hasattr(storages.get(pk=int(storage)), good):
                    continue
                # Если на Складе недостаточно товара
                if not getattr(storages.get(pk=int(storage)), good) >= int(values.get(storage).get(good)):
                    return False,\
                           storages.get(pk=int(storage)),\
                           good, int(values.get(storage).get(good)),\
                           getattr(storages.get(pk=int(storage)), good)

    return True, None, None, None, None
