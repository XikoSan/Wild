# coding=utf-8

from gov.models.president import President
from regime.regime import Regime
from state.models.parliament.parliament import Parliament
from regime.temporary import Temporary

# президентская республика
class Presidential(Regime):
    allowed_source = [
        'Temporary',
    ]

    allowed_dest = [
    ]

    government = {
        'leader': President,
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

        if not current_regime.__name__ in Presidential.allowed_source:
            return 'rj'

        # есть ли в текущем режиме парл?
        if not current_regime.government['parliament']:
            Presidential.set_parliament(state)

        # если лидер отличается от Президента
        if current_regime.government['leader'] != Presidential.government['leader']:
            Presidential.set_leader(current_regime, state)

        return 'ac'

    @staticmethod
    def set_parliament(state):

        parliament = Parliament(
            state=state
        )

        parliament.save()

    @staticmethod
    def set_leader(current_regime, state):
        # если сейчас лидера нет
        if not current_regime.government['leader']:
            leader = President(
                state=state
            )

            leader.save()
