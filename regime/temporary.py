# coding=utf-8

from regime.regime import Regime
from state.models.parliament.parliament import Parliament
from state.models.capital import Capital
from state.models.treasury import Treasury

# временное правительство
class Temporary(Regime):

    forbidden_bills = [
        'ChangeResidency'
    ]

    allowed_source = [
    ]

    allowed_dest = [
        'Presidential',
    ]

    government = {
        'leader': False,
        'parliament': Parliament,
        # 'ministry': False,
    }

    @staticmethod
    def set_regime(state):
        current_regime = None
        # получаем текущий режим из свойств госа
        for regime_cl in Regime.__subclasses__():
            if state.type == regime_cl.__name__:
                current_regime = regime_cl
                break

        if not current_regime:
            return 'rj'

        if not current_regime.__name__ in Temporary.allowed_source:
            return 'rj'

        # есть ли в текущем режиме парл?
        if not current_regime.government['parliament']:
            Temporary.set_parliament(state)

        # если есть лидер
        if current_regime.government['leader']:
            Temporary.set_leader(current_regime, state)

        return 'ac'

    @staticmethod
    def set_parliament(state):

        parliament = Parliament(
            state=state
        )

        parliament.save()

    @staticmethod
    def set_leader(current_regime, state):
        # todo: удалять лидера при помощи метода текущего режима
        pass

    @staticmethod
    def dissolution(state):
        # удаляем парламент
        if Parliament.objects.filter(state=state).exists():
            Parliament.objects.get(state=state).delete()

        # удаляем столицу как объект
        if Capital.objects.filter(state=state).exists():
            Capital.objects.get(state=state).delete()

        # удаляем казну как объект
        if Treasury.objects.filter(state=state).exists():
            tres = Treasury.objects.get(state=state)
            tres.deleted = True
            tres.save()

