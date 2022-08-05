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

# Изменить способ получения прописки в государстве
# Не оптимизировать код хоткеями - ЗАТИРАЕТ ИМПОРТЫ !!
class ChangeResidency(Bill):

    # тип государства
    residencyTypeChoices = (
        ('free', 'Свободная'),
        ('issue', 'Выдаётся министром'),
    )

    residency = models.CharField(
        max_length=5,
        choices=residencyTypeChoices,
        default='free',
    )

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeResidency.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        new_form = request.POST.get('change_residency_residency')

        choice_list = []

        for choice in ChangeResidency.residencyTypeChoices:
            choice_list.append(choice[0])

        if new_form == '':
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Тип получения прописки должен быть указан',
            }

        elif not new_form in choice_list:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Такого типа получения прописки не существует',
            }

        if new_form == parliament.state.residency:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Этот тип получения прописки уже выбран',
            }

        # ура, все проверили
        bill = ChangeResidency(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            residency=new_form,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        state.residency = self.residency
        state.save()

        ChangeResidency.objects.filter(pk=self.pk).update(type='ac', running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        data = {}

        return data, 'state/gov/drafts/change_residency.html'

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

        return data, 'state/gov/bills/change_residency.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/change_residency.html'

    def __str__(self):
        return self.get_form_display()

    # Свойства класса
    class Meta:
        verbose_name = "Новый способ выдачи прописки"
        verbose_name_plural = "Новые способы выдачи прописки"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeResidency)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
