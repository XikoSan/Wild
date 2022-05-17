# coding=utf-8

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.apps import apps
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State

from regime.regime import Regime
from regime.temporary import Temporary
from regime.presidential import Presidential

# Изменить название государства
# Не оптимизировать код хоткеями - ЗАТИРАЕТ ИМПОРТЫ !!
class ChangeForm(Bill):

    # тип государства
    stateTypeChoices = (
        ('Temporary', 'Временное правительство'),
        ('Presidential', 'Президентская республика'),
    )

    form = models.CharField(
        max_length=15,
        choices=stateTypeChoices,
        default='pres',
    )

    # возможность принять закон досрочно
    accept_ahead = False

    # процент голосов "за", который надо преодолеть, чтобы принять закон
    acceptation_percent = 80

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeForm.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        new_form = request.POST.get('new_state_form')

        choice_list = []

        for choice in ChangeForm.stateTypeChoices:
            choice_list.append(choice[0])

        if new_form == '':
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Новая форма государства должна быть указана',
            }

        elif not new_form in choice_list:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Такой формы государства не существует',
            }

        # ура, все проверили
        bill = ChangeForm(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            form=new_form,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        new_regime = None
        # получаем текущий режим из свойств госа
        for regime_cl in Regime.__subclasses__():
            if self.form == regime_cl.__name__:
                new_regime = regime_cl
                break

        b_type = new_regime.set_regime(state)

        # если закон принят
        if b_type == 'ac':
            state.type = self.form
            state.save()

        ChangeForm.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        current_regime = None
        # получаем текущий режим из свойств госа
        for regime_cl in Regime.__subclasses__():
            if state.type == regime_cl.__name__:
                current_regime = regime_cl
                break

        forms_dict = {}
        for form in ChangeForm.stateTypeChoices:
            if form[0] in current_regime.allowed_dest:
                forms_dict[form[0]] = form[1]

        data = {'forms': forms_dict}

        return data, 'state/gov/drafts/change_form.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/change_form.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/change_form.html'

    def __str__(self):
        return self.get_form_display()

    # Свойства класса
    class Meta:
        verbose_name = "Новая форма правления государства"
        verbose_name_plural = "Новые формы правления государств"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeForm)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
