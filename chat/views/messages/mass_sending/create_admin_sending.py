import json
import logging
import redis
from celery import shared_task
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from itertools import chain

from article.forms import NewArticleForm
from article.models.article import Article
from chat.dialogue_consumers import get_last_id_from_db
from chat.models.messages.chat_members import ChatMembers
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# рассылка от админа во все чаты
@shared_task(name="admin_sending")
def admin_sending(text):
    admin = Player.objects.get(pk=1)

    logger = logging.getLogger(__name__)

    try:

        chat_ids = list(ChatMembers.objects.filter(player=admin).values_list('chat_id', flat=True))

        for chat_id in chat_ids:

            timestamp = str(datetime.now().timestamp()).split('.')[0]

            message = {
                'author': admin.pk,
                'content': text,
                'dtime': timestamp,
                'read': False
            }

            redis_last_message_index = 0

            r = redis.StrictRedis(host='redis', port=6379, db=0)

            redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, 0, withscores=True)

            logger.debug(chat_id)
            logger.debug(redis_list)

            # если в редисе ничего нет, то либо чат новый, либо всё в БД
            if redis_list:
                redis_last_message_index = redis_list[0][1]
            # подглядим в БД
            else:
                redis_last_message_index = get_last_id_from_db(chat_id)

            o_json = json.dumps(message, indent=2, default=str)

            r.zadd(f'dialogue_{chat_id}', {o_json: int(redis_last_message_index) + 1})

            count = r.zcard(f'dialogue_{chat_id}')

            logger.debug(f'count: {count}')

            # сохраняем каждые 50 сообщений
            if count > 49:
                redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, -1, withscores=True)
                redis_list.reverse()

                block = MessageBlock(
                    chat=Chat.objects.get(pk=str(chat_id)),
                    messages=str(redis_list)
                )
                block.save()

                r.zremrangebyrank(f'dialogue_{chat_id}', 0, -1)

            # обновляем информацию о дате последнего сообщения
            r.hset('chat_mess_dates', chat_id, int(timestamp))

            # каждому получателю сообщений, кроме автора повышаем счетчик непрочитанного
            for chat_mem in ChatMembers.objects.filter(chat__pk=chat_id).exclude(player__pk__in=[admin.pk, ]):
                unread = 0

                unread_redis = r.hget(f'chats_{chat_mem.player.pk}_unread', chat_id)

                if unread_redis:
                    unread = int(unread_redis)

                r.hset(f'chats_{chat_mem.player.pk}_unread', chat_id, unread + 1)

    except Exception as e:

        logger.exception('Произошла нештатная ситуация:')


# открыть статью
@login_required(login_url='/')
@check_player
def create_admin_sending(request):
    if request.method == "POST":

        if not request.user.is_superuser:
            data = {
                'response': 'Недостаточно прав',
                'header': 'Новая рассылка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        admin_sending.delay(request.POST.get('message'))

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Новая рассылка',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
