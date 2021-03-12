from storage.models.good_lock import Storage, GoodLock


# проверка наличия места для товаров на указанном Складе, перед начислением их туда
# входные данные:
# qset - Queryset со Складами, которые нужно обработать

# выходные данные:
# Queryset со Складами, к которым применены блокировки

# выходные данные:
# price    - цена перевозки
def get_storages(qset):
    lock_result = GoodLock.objects.filter(lock_storage__in=qset)
    # по каждому складу осн выборки
    for super_line in qset:
        # по всем блокировкам этого склада
        for lock_line in lock_result.filter(lock_storage=super_line):
            setattr(super_line, getattr(lock_line, 'lock_good'),
                    getattr(super_line, getattr(lock_line, 'lock_good')) + lock_line.lock_count)

    return qset
