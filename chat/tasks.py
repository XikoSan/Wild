from celery import shared_task
from django_celery_beat.models import PeriodicTask
import redis
from chat.models.messages.chat import Chat
from chat.models.messages.message_block import MessageBlock

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

    