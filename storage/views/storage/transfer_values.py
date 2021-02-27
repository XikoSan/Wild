from math import ceil

from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport


# Начисление товаров на целевой Склад
# входные данные:
# dest     - целевой склад
# values   - формат данных JSON из запроса
def transfer_values(dest, values):
    # словарь со списком всех складов-источников
    source_dict = {}
    # словарь со списком всех Транспортов
    transport_dict = {}
    # словарь со списоком всего что передают
    # "товар" - "количество"
    transfer_dict = {}
    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            source_dict[storage] = Storage.objects.get(pk=int(storage))
            transport_dict[storage] = Transport(player=dest.owner, storage_from=Storage.objects.get(pk=int(storage)),
                                                storage_to=dest)
            # идём по списку товаров
            for good in values.get(storage):
                # списываем со склада-источника ресурсы
                setattr(source_dict[storage], good,
                        getattr(source_dict[storage], good) - int(values.get(storage).get(good)))
                # добавляем в транспорт запись об объёме
                setattr(transport_dict[storage], good, int(values.get(storage).get(good)))
                # о количестве кубов
                # надо понять, к какой категории относится товар. Так что, придётся пройтись по циклу
                # "minerals" - "oils" - "materials" - "units"
                for cat in ["minerals", "oils", "materials", "units"]:
                    if good in getattr(Transport, cat):
                        setattr(transport_dict[storage], good + '_vol',
                                ceil(int(values.get(storage).get(good)) * getattr(Transport, cat)[good]))
                # если значение в словаре целевого склада уже есть - дополняем
                if transfer_dict.get(good):
                    transfer_dict[good] += int(values.get(storage).get(good))
                else:
                    transfer_dict[good] = int(values.get(storage).get(good))

    # списываем ресурсы со всех складов-источников
    for s_storage in source_dict:
        source_dict[s_storage].save()
    # для каждого товара каждого Транспорта считаем сумму объемов и сохраняем
    for transport in transport_dict:
        for cat in ["minerals", "oils", "materials", "units"]:
            for good in getattr(transport_dict[transport], cat):
                if getattr(transport_dict[transport], good + '_vol') > 0:
                    setattr(transport_dict[transport], 'total_vol',
                            getattr(transport_dict[transport], 'total_vol') + getattr(transport_dict[transport],
                                                                                      good + '_vol'))
        transport_dict[transport].save()
    # начисляем ресурсы целевому складу
    for i_good in transfer_dict:
        setattr(dest, i_good, getattr(dest, i_good) + int(transfer_dict[i_good]))
    dest.save()
