# coding=utf-8

from django.apps import apps
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext

from bill.models.bill import Bill
from regime.presidential import Presidential
from regime.regime import Regime
from regime.temporary import Temporary
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State
from django.utils.translation import pgettext_lazy


# Изменить название государства
# Не оптимизировать код хоткеями - ЗАТИРАЕТ ИМПОРТЫ !!
class ChangeForm(Bill):
    # тип государства
    stateTypeChoices = (
        ('Temporary', pgettext_lazy('new_bill', 'Временное правительство')),
        ('Presidential', pgettext_lazy('new_bill', 'Президентская республика')),
    )

    form = models.CharField(
        max_length=15,
        choices=stateTypeChoices,
        default='pres',
    )

    # возможность принять закон досрочно
    accept_ahead = False

    # процент голосов "за", который надо преодолеть, чтобы принять закон
    acceptation_percent = 75

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeForm.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        new_form = request.POST.get('new_state_form')

        choice_list = []

        for choice in ChangeForm.stateTypeChoices:
            choice_list.append(choice[0])

        if new_form == '':
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Новая форма государства должна быть указана'),
            }

        elif not new_form in choice_list:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Такой формы государства не существует'),
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

    @staticmethod
    def get_new_draft(state):
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

        return data, 'state/redesign/drafts/change_form.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/change_form.html'

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/change_form.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/change_form.html'

    # получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/change_form.html'

    def __str__(self):
        return self.get_form_display()

    # Свойства класса
    class Meta:
        verbose_name = pgettext_lazy('new_bill', "Новая форма правления государства")
        verbose_name_plural = pgettext_lazy('new_bill', "Новые формы правления государств")

# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeForm)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ChangeForm)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
