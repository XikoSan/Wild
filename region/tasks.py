import json
from celery import shared_task, current_app
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from player.logs.auto_mining import AutoMining
from player.player import Player
from chat.dialogue_consumers import _append_message
from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from gov.models.president import President
from django.utils.translation import pgettext

# перелет игрока в другой регион
@shared_task(name="move_to_another_region")
def move_to_another_region(id):
    player = Player.get_instance(pk=id)
    prev_region = player.region

    player.region = player.destination
    player.destination = None
    player.arrival = timezone.now()
    player.task.clocked.delete()
    player.task = None
    player.save()
    player.increase_calc()

    if player.region.state and not player.region.state == prev_region.state:
        if President.objects.filter(state=player.region.state).exists():
            pres_post = President.objects.get(state=player.region.state)
            # если на посту есть игрок
            if pres_post.leader:

                if not pres_post.leader == player:

                    pres_chat = Chat.objects.create()
                    pres_chat_id = pres_chat.pk

                    member, created = ChatMembers.objects.get_or_create(
                        chat=pres_chat,
                        player=pres_post.leader,
                    )
                    member, created = ChatMembers.objects.get_or_create(
                        chat=pres_chat,
                        player=player,
                    )

                    if not player.region.state.message:
                        pres_text = pgettext('start_messages', "Добро пожаловать в государство %(state_title)s! Это автоматическое сообщение, созданное игрой. Но вы можете связаться со мной напрямую, просто ответив на него") % {"state_title": player.region.state }
                    else:
                        pres_text = player.region.state.message

                    _append_message(chat_id=pres_chat_id, author=pres_post.leader, text=pres_text)


# сбор есст. прироста раз в десять минут
@shared_task(name="crude_retrieve")
def crude_retrieve(id):
    if AutoMining.objects.filter(pk=id).exists():
        AutoMining.objects.get(pk=id).retrieve_crude()
    else:
        PeriodicTask.objects.filter(task="crude_retrieve", args=json.dumps([id])).delete()
