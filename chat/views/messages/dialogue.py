import datetime
import json
import os
import pytz
import random
import redis
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from chat.dialogue_consumers import _mark_as_read
from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.message_block import MessageBlock
from django.utils.translation import pgettext
from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import TIME_ZONE


# преобразует последовательность из памяти в сообщения
def tuple_to_messages(player, messages, tuple, r):
    for scan in tuple:
        b = json.loads(scan[0])

        if not Player.objects.filter(pk=int(b['author'])).exists():
            r.zremrangebyscore('chat', int(scan[1]), int(scan[1]))
            continue

        author = Player.objects.filter(pk=int(b['author'])).only('id', 'nickname', 'image', 'time_zone').get()
        # сначала делаем из наивного времени aware, потом задаем ЧП игрока
        b['dtime'] = datetime.datetime.fromtimestamp(int(b['dtime'])).astimezone(
            tz=pytz.timezone(player.time_zone)).strftime("%d.%m.%y %H:%M")
        b['author'] = author.pk
        b['counter'] = int(scan[1])
        if len(author.nickname) > 25:
            b['author_nickname'] = f'{ author.nickname[:25] }...'
        else:
            b['author_nickname'] = author.nickname
        if author.image:
            b['image_link'] = author.image.url
        else:
            b['image_link'] = 'nopic'

        b['user_pic'] = False
        # если сообщение - ссылка на изображение
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if any(extension in b['content'].lower() for extension in image_extensions):
            b['user_pic'] = True

        messages.append(b)

    return messages


@login_required(login_url='/')
@check_player
# Открытие страницы диалога с персонажем
def dialogue(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)
    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)
    # если игрок хочет посмотреть самого себя
    if player == char:
        # перекидываем его в сообщения
        return redirect("dialogues")

    messages = []

    stickers_dict = {}
    stickers_header_dict = {}
    header_img_dict = {}

    if not player.chat_ban:

        chat_id = None
        blocks_pk = []

        player1_chats = ChatMembers.objects.filter(player=player).values('chat')
        player2_chats = ChatMembers.objects.filter(player=char).values('chat')
        common_chats = player1_chats.intersection(player2_chats)

        if common_chats:
            chat_id = common_chats[0]['chat']

        else:
            chat = Chat.objects.create()
            chat_id = chat.pk

            member, created = ChatMembers.objects.get_or_create(
                chat=chat,
                player=player,
            )
            member, created = ChatMembers.objects.get_or_create(
                chat=chat,
                player=char,
            )

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        # counter = 0
        # if r.hlen('counter') > 0:
        #     counter = r.hget('counter', 'counter')
        redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, -1, withscores=True)
        redis_list.reverse()

        # если в ОЗУ лежит меньше 50 сообщений, и есть сообщения в БД
        if len(redis_list) < 50 and MessageBlock.objects.filter(chat=int(chat_id)).exists():
            # все блоки сообщений, которые мы набрали на вывод
            messages_arch = []
            # суммарная длина этих блоков
            messages_db_total = 0

            for mess_block in MessageBlock.objects.only("pk").filter(chat=int(chat_id)).order_by('-date'):

                block = MessageBlock.objects.get(pk=mess_block.pk)
                blocks_pk.append(block.pk)
                redis_dump = eval(block.messages)

                # добавляем сообщения из БД
                tmp_messages = []
                tuple_to_messages(player, tmp_messages, redis_dump, r)

                messages_arch.append(tmp_messages)

                messages_db_total += len(tmp_messages)

                if messages_db_total + len(redis_list) >= 50:
                    break

            messages_arch.reverse()
            for messages_block in messages_arch:
                messages += messages_block

        # добавляем сообщения из ОЗУ на выход
        tuple_to_messages(player, messages, redis_list, r)

        stickers = StickersOwnership.objects.filter(owner=player)

        for sticker_own in stickers:
            # название пака
            stickers_header_dict[sticker_own.pack.pk] = sticker_own.pack.title
            #  получим рандомную картинку для заголовка
            header_img_dict[sticker_own.pack.pk] = random.choice(
                Sticker.objects.filter(pack=sticker_own.pack)).image.url
            # все остальные картинки - в словарь
            stickers_dict[sticker_own.pack.pk] = Sticker.objects.filter(pack=sticker_own.pack)

    else:
        # перекидываем его в сообщения
        return redirect("overview")

    http_use = False
    if os.getenv('HTTP_USE'):
        http_use = True

    page = 'chat/dialogue.html'

    return render(request, page, {
        'page_name': pgettext('chat', "Диалог с %(nickname)s") % {"nickname": char.nickname},

        'player': player,
        'char': char,

        'chat_id': chat_id,
        'messages': messages,
        'blocks_pk': blocks_pk,

        'stickers_header_dict': stickers_header_dict,
        'header_img_dict': header_img_dict,
        'stickers_dict': stickers_dict,

        'http_use': http_use,
    })
