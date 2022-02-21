from django import template

register = template.Library()
from state.models.treasury import Treasury
from storage.models.storage import Storage
from state.models.treasury_lock import TreasuryLock


@register.inclusion_tag('state/gov/treasury.html')
def treasury(state):
    treasury = None

    if Treasury.objects.filter(state=state).exists():
        # находим казну государства
        treasury = Treasury.get_instance(state=state)

        locks = {}
        for lock in TreasuryLock.actual.filter(lock_treasury=treasury):
            if lock.lock_good in locks.keys():
                locks[lock.lock_good] += lock.lock_count
            else:
                locks[lock.lock_good] = lock.lock_count

    return {
        # казна
        'treasury': treasury,
        # класс склада
        'storage_cl': Storage,
        # блокировки
        'locks': locks,
    }
