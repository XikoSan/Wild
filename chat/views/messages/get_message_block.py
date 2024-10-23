import json
import redis
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import pgettext
from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from chat.models.messages.message_block import MessageBlock
from chat.views.messages.dialogue import tuple_to_messages
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# покупка стикерпака
@login_required(login_url='/')
@check_player
@transaction.atomic
def get_message_block(request):
    if request.method == "POST":
        try:
            room_id = int(request.POST.get('room'))

        except ValueError:
            return {
                'response': pgettext('chat', 'ID комнаты должен быть целым числом'),
                'header': pgettext('chat', 'Получение сообщений'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        if not Chat.objects.filter(pk=room_id).exists():
            data = {
                'response': pgettext('chat', 'Указанная комната не найдена'),
                'header': pgettext('chat', 'Получение сообщений'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # получаем чат
        chat = Chat.objects.get(pk=room_id)

        # проверяем, что игрок состоит в этом чате
        members = ChatMembers.objects.filter(chat=chat)
        if not members.filter(player=player).exists():
            data = {
                'response': pgettext('chat', 'Вы не состоите в этом чате'),
                'header': pgettext('chat', 'Получение сообщений'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # Находим блок сообщений, исключая переданные
        loaded_pk = json.loads(request.POST.get('loaded'))
        messages = []
        block = MessageBlock.objects.filter(chat=int(room_id)).exclude(pk__in=loaded_pk).order_by('-date').first()

        if block:
            messages_tuple = eval(block.messages)

            # добавляем сообщения из БД на выход
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            messages = tuple_to_messages(player, messages, messages_tuple, r)

            data = {
                'response': 'ok',
                'block_pk': block.pk,
                'messages': messages,
            }
            return JResponse(data)

        else:
            data = {
                'response': 'empty',
            }
            return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('chat', 'Получение сообщений'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
