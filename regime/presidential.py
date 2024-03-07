# coding=utf-8

from django.utils import timezone

from gov.models.president import President
from regime.regime import Regime
from regime.temporary import Temporary
from state.models.capital import Capital
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury


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

    forbidden_bills = []

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

        parl = Parliament.objects.get(state=state)
        DeputyMandate.objects.create(parliament=parl, is_president=True)

        # если сейчас лидера нет
        if not current_regime.government['leader']:
            leader = President(
                state=state
            )
            leader.foundation_date = timezone.now()
            leader.elections_day = leader.foundation_date.weekday()

            leader.save()

    @staticmethod
    def dissolution(state):
        # удаляем парламент
        if Parliament.objects.filter(state=state).exists():
            Parliament.objects.get(state=state).delete()

        # удаление президента как объект
        if President.objects.filter(state=state).exists():
            President.objects.get(state=state).delete()

        # удаляем столицу как объект
        if Capital.objects.filter(state=state).exists():
            Capital.objects.get(state=state).delete()

        # удаляем казну как объект
        if Treasury.objects.filter(state=state).exists():
            tres = Treasury.objects.get(state=state)
            tres.deleted = True
            tres.save()
