from player.player import Player
from storage.models.storage import Storage
from storage.models.stock import Stock
from storage.models.good import Good
from storage.views.storage.locks.get_storage import get_stocks


# проверка наличия места для товаров на указанном Складе, перед начислением их туда
# входные данные:
# dest     - целевой склад, емкость которого надо проверять
# values   - формат данных JSON из запроса

# выходные данные:
# status   - всё ОК или нет
# good     - имя товара, для которого не хватает места
# sent     - сколько отправляют товара
# exist_cap- сколько есть свободного места
def check_cap_exists(dest, values):

    # список айдишников запасов, которые будем обрабатывать
    stocks_pk_list = []
    # сквозной словарь: айдишник Запаса - сколько хотят передать
    stocks_summs = {}

    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идем по списку запасов
            for stock_pk in values.get(storage):
                # собираем айдишники запасов
                stocks_pk_list.append(stock_pk)
                # получаем число в сквозной словарь
                stocks_summs[int(stock_pk)] = int(values[storage][stock_pk])

    stocks = Stock.objects.filter(pk__in=stocks_pk_list)

    # список имен товаров на передачу
    goods = []
    # количество передаваемых товаров по типоразмерам
    sums_by_cap = {}

    for stock in stocks:
        # получаем имя товара, которые нужно узнать
        if not stock.good.name_ru in goods:
            goods.append(stock.good.name_ru)
        # суммируем передаваемые товары по их типоразмерам
        if stock.good.size in sums_by_cap:
            sums_by_cap[stock.good.size] += stocks_summs[stock.pk]
        else:
            sums_by_cap[stock.good.size] = stocks_summs[stock.pk]

    # словарь запасов: товар - запасы (с блокировками)
    # словарь емкостей: типоразмер - занятое пространство
    ret_stocks, ret_cap_stocks = get_stocks(dest, goods)

    for size in Good.sizeChoices:
        if size[0] in ret_cap_stocks and size[0] in sums_by_cap:
            if ret_cap_stocks[size[0]] + sums_by_cap[size[0]] > getattr(dest, size[0] + '_cap'):
                # флаг ошибки
                # название типоразмера
                # требуемый свободный объём
                # фактический свободный объем
                return False,\
                       size[1],\
                       sums_by_cap[size[0]],\
                       getattr(dest, size[0] + '_cap') - ret_cap_stocks[size[0]]

    return True, None, None, None
