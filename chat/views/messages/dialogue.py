import datetime
import json
import pytz
import random
import os
import redis
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from chat.models.sticker import Sticker
from chat.models.stickers_ownership import StickersOwnership
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import TIME_ZONE

from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.chat import Chat

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
        return redirect("messages")

    messages = []

    stickers_dict = {}
    stickers_header_dict = {}
    header_img_dict = {}

    if not player.chat_ban:

        chat_id = None

        player1_chats = ChatMembers.objects.filter(player=player).values('chat')
        player2_chats = ChatMembers.objects.filter(player=char).values('chat')
        common_chats = player1_chats.intersection(player2_chats)

        if common_chats:
            chat_id = common_chats[0]['chat']

        else:
            chat = Chat.objects.create()
            chat_id = chat.pk

            member, created = ChatMembers.objects.get_or_create(
                chat = chat,
                player = player,
            )
            member, created = ChatMembers.objects.get_or_create(
                chat = chat,
                player = char,
            )

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        # counter = 0
        # if r.hlen('counter') > 0:
        #     counter = r.hget('counter', 'counter')
        from player.logs.print_log import log

        redis_list = r.zrevrange(f'dialogue_{chat_id}', 0, -1, withscores=True)
        redis_list.reverse()

        log(redis_list)

        for scan in redis_list:
            b = json.loads(scan[0])

            if not Player.objects.filter(pk=int(b['author'])).exists():
                r.zremrangebyscore('chat', int(scan[1]), int(scan[1]))
                continue

            author = Player.objects.filter(pk=int(b['author'])).only('id', 'nickname', 'image', 'time_zone').get()
            # сначала делаем из наивного времени aware, потом задаем ЧП игрока
            b['dtime'] = datetime.datetime.fromtimestamp(int(b['dtime'])).astimezone(
                tz=pytz.timezone(player.time_zone)).strftime("%H:%M")
            b['author'] = author.pk
            b['counter'] = int(scan[1])
            b['author_nickname'] = author.nickname
            if author.image:
                b['image_link'] = author.image.url
            else:
                b['image_link'] = 'nopic'

            messages.append(b)

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
        'player': player,
        'char': char,

        'chat_id': chat_id,
        'messages': messages,

        'stickers_header_dict': stickers_header_dict,
        'header_img_dict': header_img_dict,
        'stickers_dict': stickers_dict,

        'http_use': http_use,
    })
