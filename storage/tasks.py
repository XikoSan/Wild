from celery import shared_task
from django_celery_beat.models import PeriodicTask

from storage.models.auction.auction import BuyAuction


@shared_task(name="run_auction")
def run_auction(auction_pk):
    auction = BuyAuction.objects.get(pk=auction_pk)

    auction.run()

    task_identificator = auction.task.id
    # убираем таску у экземпляра модели
    BuyAuction.objects.select_related('task').filter(pk=auction_pk).update(task=None, deleted=True)
    # удаляем таску
    PeriodicTask.objects.filter(pk=task_identificator).delete()
