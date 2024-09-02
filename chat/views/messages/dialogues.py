import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.message_block import Chat
from chat.models.messages.message_block import MessageBlock
from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from chat.views.messages.dialogue import tuple_to_messages


# сообщения игрока
# page - открываемая страница
@login_required(login_url='/')
@check_player
def dialogues(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем чаты, в которых он состоит
    member_at = ChatMembers.objects.filter(player=player).values_list("chat__pk")
    # ID чатов
    chats_pk = []
    for member in member_at:
        chats_pk.append(member[0])

    # список айди диалогов от свежего к старому
    dialogs = []

    # ID диалога:
    # + аватар собседедника
    # + ник собеседника
    # + ID собеседника (кликать на аватар для открытия страницы)
    # + дата последнего сообщения
    # + текст последнего сообщения
    # + признак непрочитанного диалога (из redis)
    dialogs_data = {}

    from player.logs.print_log import log

    log('tick 1')

    if chats_pk:
        # по айдишникам чатов получаем даты последних сообщений
        r = redis.StrictRedis(host='redis', port=6379, db=0)
        chats_timestamps = r.hmget('chat_mess_dates', chats_pk)

        # складываем даты и ID сообщений в единый кортеж, чтобы упорядочить
        chats_tuple = []

        cycle = 0
        for chat in chats_pk:
            timestamp = chats_timestamps[cycle]
            if not timestamp:
                timestamp = 0
            chats_tuple.append((chat, int(timestamp)))
            cycle += 1

        # сортируем tuple по timestamp. Чем он больше - тем новее диалог
        sorted_tuples = sorted(chats_tuple, key=lambda x: x[1], reverse=True)

        log('tick 2')

        sorted_tuples = sorted_tuples[:50]

        # получим собеседников
        companions = ChatMembers.objects.filter(chat__pk__in=chats_pk).exclude(player=player)

        log('tick 3')

        lopp = 1

        # берем последние сообщения последних 50 чатов
        for dialog in sorted_tuples:

            log(f'tick 4 loop {lopp}')
            messages = []

            dialogs.append(dialog[0])
            dialogs_data[dialog[0]] = {}
            # число непрочитанных собщений в этом диалоге
            read = True
            unread_redis = r.hget(f'chats_{player.pk}_unread', dialog[0])

            if unread_redis and int(unread_redis) > 0:
                read = False
            dialogs_data[dialog[0]]['read'] = read

            #  последнее сообщение из Redis
            redis_list = r.zrevrange(f'dialogue_{dialog[0]}', 0, 0, withscores=True)

            if not redis_list:
                if MessageBlock.objects.filter(chat__pk=dialog[0]).exists():
                    #  последнее сообщение из БД
                    block = MessageBlock.objects.filter(chat__pk=dialog[0]).order_by('-date').first()
                    redis_dump = eval(block.messages)
                    tuple_to_messages(player, messages, redis_dump, r)

                    dialogs_data[dialog[0]]['dtime'] = messages[-1]['dtime']
                    dialogs_data[dialog[0]]['content'] = messages[-1]['content']
                    # если последнее сообщение принадлежит собсеседнику
                    if messages[-1]['author'] != player.pk:
                        dialogs_data[dialog[0]]['author'] = messages[-1]['author']
                        dialogs_data[dialog[0]]['author_nickname'] = messages[-1]['author_nickname']
                        dialogs_data[dialog[0]]['image_link'] = messages[-1]['image_link']

                else:
                    # вообще нет сообщений в диалоге
                    dialogs_data[dialog[0]]['dtime'] = None
                    dialogs_data[dialog[0]]['content'] = None

            else:
                tuple_to_messages(player, messages, redis_list, r)
                dialogs_data[dialog[0]]['dtime'] = messages[-1]['dtime']
                dialogs_data[dialog[0]]['content'] = messages[-1]['content']
                # если последнее сообщение принадлежит собсеседнику
                if messages[-1]['author'] != player.pk:
                    dialogs_data[dialog[0]]['author'] = messages[-1]['author']
                    dialogs_data[dialog[0]]['author_nickname'] = messages[-1]['author_nickname']
                    dialogs_data[dialog[0]]['image_link'] = messages[-1]['image_link']

            # если последнее сообщение принадлежало не собсеседнику - ищем аву, ник, ID
            if companions.filter(chat__pk=dialog[0]).exists():
                companion = companions.get(chat__pk=dialog[0])

                dialogs_data[dialog[0]]['author'] = companion.player.pk
                dialogs_data[dialog[0]]['author_nickname'] = companion.player.nickname
                if companion.player.image:
                    dialogs_data[dialog[0]]['image_link'] = companion.player.image.url
                else:
                    dialogs_data[dialog[0]]['image_link'] = 'nopic'

            else:
                dialogs_data[dialog[0]]['author'] = None
                dialogs_data[dialog[0]]['author_nickname'] = 'Удаленный аккаунт'
                dialogs_data[dialog[0]]['image_link'] = 'nopic'

            lopp += 1

    log(dialogs_data)
    log('tick 5')

    # отправляем в форму
    return render(request, 'chat/dialogues.html', {
        'page_name': _('Диалоги'),

        'player': player,

        'dialogs': dialogs,
        'dialogs_data': dialogs_data,
    })
