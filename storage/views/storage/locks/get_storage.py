import copy

from storage.models.good_lock import Storage, GoodLock


# получение Склада с блокировками ресурсов, для вычисления доступного места
# входные данные:
# storage - Склада, который нужно обработать

# выходные данные:
# Склад, к которому применены блокировки
def get_storage(storage, resources):
    ret_storage = copy.deepcopy(storage)
    if resources:
        lock_result = GoodLock.actual.filter(lock_storage=ret_storage, lock_good__in=resources)
    else:
        lock_result = GoodLock.actual.filter(lock_storage=ret_storage)
    # по всем блокировкам этого склада
    for lock_line in lock_result.filter(lock_storage=ret_storage):
        setattr(ret_storage, getattr(lock_line, 'lock_good'),
                getattr(ret_storage, getattr(lock_line, 'lock_good')) + lock_line.lock_count)

    return ret_storage
