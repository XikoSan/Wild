from player.player import Player
from storage.models.storage import Storage
from storage.models.stock import Stock
from storage.models.good import Good


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

    # список айдишников запасов, которые будем обрабатывать
    stocks_pk_list = []
    # сквозной словарь: айдишник Запаса - сколько хотят передать
    stocks_summs = {}

    # идем по всем складам
    for storage_pk in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage_pk)):
            # идем по списку запасов
            for stock_pk in values.get(storage_pk):
                # собираем айдишники запасов
                stocks_pk_list.append(stock_pk)
                # получаем число в сквозной словарь
                stocks_summs[int(stock_pk)] = int(values[storage_pk][stock_pk])

    stocks = Stock.objects.filter(pk__in=stocks_pk_list)

    for stock in stocks:
        if not stock.stock >= stocks_summs[stock.pk]:
            return False,\
                   stock.storage,\
                   stock.good.name,\
                   stocks_summs[stock.pk],\
                   stock.stock

    # # идем по всем складам
    # for storage in values.keys():
    #     # если в текущем Складе есть ресурсы
    #     if len(values.get(storage)):
    #         # идём по списку товаров
    #         for good in values.get(storage):
    #             # проверка, существует ли такой ресурс вообще
    #             if not hasattr(storages.get(pk=int(storage)), good):
    #                 continue
    #             # Если на Складе недостаточно товара
    #             if not getattr(storages.get(pk=int(storage)), good) >= int(values.get(storage).get(good)):
    #                 return False,\
    #                        storages.get(pk=int(storage)),\
    #                        good, int(values.get(storage).get(good)),\
    #                        getattr(storages.get(pk=int(storage)), good)
    #
    return True, None, None, None, None
