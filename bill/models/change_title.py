# coding=utf-8

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State
from django.utils.translation import pgettext
from django.utils.translation import pgettext_lazy


# Изменить название государства
class ChangeTitle(Bill):
    # название страны
    new_title = models.CharField(max_length=50, verbose_name='Название государства')

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeTitle.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        new_title = request.POST.get('new_title')

        if new_title == '':
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Новое название не должно быть пустым'),
            }
        else:
            new_title = new_title[:50]

        # ура, все проверили
        bill = ChangeTitle(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            new_title=new_title,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        if self.new_title != '':
            state.title = self.new_title
            b_type = 'ac'

        else:
            b_type = 'rj'

        # если закон принят
        if b_type == 'ac':
            self.save()
            state.save()

        ChangeTitle.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        data = {}

        return data, 'state/gov/drafts/change_title.html'

    @staticmethod
    def get_new_draft(state):

        data = {}

        return data, 'state/redesign/drafts/change_title.html'

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

        return data, 'state/gov/bills/change_title.html'

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

        return data, 'state/redesign/bills/change_title.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/change_title.html'

    # получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/change_title.html'

    def __str__(self):
        return self.new_title

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Переименование государства")
        verbose_name_plural = pgettext_lazy('new_bill', "Переименования государств")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeTitle)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ChangeTitle)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()