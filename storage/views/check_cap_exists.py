from player.player import Player
from storage.models.storage import Storage


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

    # словарь со списоком всего что передают
    # "товар" - "количество"
    transfer_dict = {}
    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идём по списку товаров
            for good in values.get(storage):
                if transfer_dict.get(good):
                    transfer_dict[good] += int(values.get(storage).get(good))
                else:
                    transfer_dict[good] = int(values.get(storage).get(good))

    for i_good in transfer_dict:
        if getattr(dest, i_good) + int(transfer_dict[i_good]) > getattr(dest, i_good + '_cap'):
            return False, Storage._meta.get_field(i_good).verbose_name.title(), transfer_dict[i_good], getattr(dest, i_good + '_cap') - getattr(dest, i_good)

    return True, None, None, None
