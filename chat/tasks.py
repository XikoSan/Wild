from celery import shared_task
from django_celery_beat.models import PeriodicTask
import redis
from chat.models.messages.chat import Chat
from chat.models.messages.message_block import MessageBlock
from article.models.article import Article
from django.utils import timezone
import datetime
from django.db.models import Q

# сохраняем чаты в БД, чтобы не болтались в ОЗУ вечность
@shared_task(name="save_chats")
def save_chats():
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    for chat in Chat.objects.all():
        chat_id = chat.pk

        if r.zcard(f'dialogue_{chat_id}') > 0:

            redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, -1, withscores=True)
            redis_list.reverse()

            block = MessageBlock(
                chat=Chat.objects.get(pk=str(chat_id)),
                messages=str(redis_list)
            )
            block.save()

            r.zremrangebyrank(f'dialogue_{chat_id}', 0, -1)


# удаляем комментарии к статьям, чтобы не болтались в ОЗУ вечность
@shared_task(name="remove_comments")
def remove_comments():
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    for article in Article.objects.defer('body').filter(
            Q(date__lt=timezone.now() - datetime.timedelta(days=1))
            & Q(date__gte=timezone.now() - datetime.timedelta(days=3))
                                                        ).values('pk'):

        r.delete(f'comments_{article["pk"]}')
        r.delete(f'counter_{article["pk"]}')

    