# coding=utf-8
import datetime
import pytz
import random
import traceback
from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import pgettext

from chat.dialogue_consumers import _append_message
from chat.models.messages.chat import Chat
from chat.models.messages.chat_members import ChatMembers
from gov.models.president import President
from player.forms import ImageForm
from player.forms import NewPlayerForm
from player.game_event.game_event import GameEvent
from player.lootbox.lootbox import Lootbox
from player.models.medal import Medal
from player.player import Player
from region.building.hospital import Hospital
from region.models.region import Region
from storage.models.stock import Stock, Good
from storage.models.storage import Storage
# from django.db.models import F
from wild_politics.settings import JResponse
from player.views.multiple_sum import multiple_sum


# Функция создания нового персонажа
def player_create(request, form):
    # Создаем нового игрока
    character = form.save(commit=False)
    character.account = request.user
    character.save()

    # settings = PlayerSettings(player=character)
    #     # settings.save()

    if Region.objects.filter(limit_id__gt=0).exists():
        start_pk = random.choice(Region.objects.filter(limit_id__gt=0))
    else:
        start_pk = random.choice(Region.objects.all())
    # Помещаем нового персонажа в случаный регион и прописываем там же
    character.region = start_pk
    character.residency = start_pk
    character.premium = timezone.now() + datetime.timedelta(days=7)

    character.cash = multiple_sum(character.cash)

    med_top = 1
    if Hospital.objects.filter(region=character.region).exists():
        med_top = Hospital.objects.get(region=character.region).top

    character.last_top = med_top
    character.save()

    storage = Storage(owner=character, region=character.region)
    storage.save()

    if Good.objects.filter(name_ru='BCAA').exists() \
            and Good.objects.filter(name_ru='Глицин').exists() \
            and Good.objects.filter(name_ru='Мельдоний').exists():
        # выдаем игроку стартовые бустеры
        for good in [Good.objects.get(name_ru='BCAA'), Good.objects.get(name_ru='Глицин'),
                     Good.objects.get(name_ru='Мельдоний')]:
            stock = Stock(
                storage=storage,
                stock=1,
                good=good
            )
            stock.save()

    # mess = Message(player_from=Player.objects.get(pk=1), player_to=character, body=_(
    #     'Welcome! I am the creator and administrator of this game. This message was created automatically - but you can reply to me, ask your question right here, or by contacting me through VK/Discord. I highly recommend reading the “First Steps” article on the Wiki, and joining one of the parties in your state’s parliament. If you have any difficulties with the game or with team finding - write to me, I will help. Also, I will be glad to feedback. Have a nice game!'),
    #                new=True)
    # mess.save()

    chat = Chat.objects.create()
    chat_id = chat.pk

    if Player.objects.filter(pk=1).exists():
        admin = Player.objects.only('id').get(pk=1)

        member, created = ChatMembers.objects.get_or_create(
            chat=chat,
            player=admin,
        )
        member, created = ChatMembers.objects.get_or_create(
            chat=chat,
            player=character,
        )

        _append_message(chat_id=chat_id, author=admin, text=pgettext('start_messages',
                                                                     'Добро пожаловать в Wild Politics! Вы всегда можете обратиться ко мне прямо в этом чате - либо связаться со мной через группу игры ВК или чат в Телеграмм. Я открыт к любым вопросам и пожеланиям.'))
        _append_message(chat_id=chat_id, author=admin, text=pgettext('start_messages',
                                                                     'Если найдётся время, расскажите, пожалуйста, о своих впечатлениях от игры - мне это важно. Приятной игры!'))

    if character.region.state:
        if President.objects.filter(state=character.region.state).exists():
            pres_post = President.objects.get(state=character.region.state)
            # если на посту есть игрок
            if pres_post.leader:

                pres_chat = Chat.objects.create(state=character.region.state)
                pres_chat_id = pres_chat.pk

                member, created = ChatMembers.objects.get_or_create(
                    chat=pres_chat,
                    player=pres_post.leader,
                )
                member, created = ChatMembers.objects.get_or_create(
                    chat=pres_chat,
                    player=character,
                )

                if not character.region.state.message:
                    pres_text = pgettext('start_messages',
                                         "Добро пожаловать в государство %(state_title)s! Это автоматическое сообщение, созданное игрой. Но вы можете связаться со мной напрямую, просто ответив на него") % {
                                    "state_title": character.region.state}
                else:
                    pres_text = character.region.state.message

                _append_message(chat_id=pres_chat_id, author=pres_post.leader, text=pres_text)

    # if GameEvent.objects.filter(running=True, type='ny', event_start__lt=timezone.now(), event_end__gt=timezone.now()).exists():
    # if Lootbox.objects.filter(player=character).exists():
    #     lbox = Lootbox.objects.get(player=character)
    # else:
    #     lbox = Lootbox(player=character)
    #
    # lbox.stock += 3
    # lbox.save()

    medal = Medal(player=character, count=1, type='public')
    medal.save()

    return character


# новый персонаж
@login_required(login_url='/')
@transaction.atomic
def new_player(request):
    # если у игрока есть хоть один персонаж:
    if Player.objects.filter(account=request.user).exists():
        # возврат в главное меню
        return redirect('edu_overview')

    else:
        # Если форма нового персонажа возвращена заполненной
        common = pytz.common_timezones
        # the name of the default time zone
        default = timezone.get_default_timezone_name()
        if request.method == "POST":
            form = NewPlayerForm(request.POST, request.FILES)
            # если форма заполненна корректно
            if form.is_valid():
                sid = transaction.savepoint()

                # Создаем его персонажа и перенаправляем в Overview
                character = player_create(request, form)

                if character.image:
                    try:
                        x = float(request.POST.get('x'))
                        y = float(request.POST.get('y'))
                        w = float(request.POST.get('width'))
                        h = float(request.POST.get('height'))

                        image = Image.open(character.image)
                        cropped_image = image.crop((x, y, w + x, h + y))
                        resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)
                        resized_image.save(character.image.path)

                    except Exception as e:
                        transaction.savepoint_rollback(sid)
                        data = {
                            'response': str(type(e).__name__) + ': ' + pgettext('new_player', 'попробуйте создать персонажа, не загружая изображение'),

                            'header': pgettext('new_player', 'Новый персонаж'),
                            'grey_btn': pgettext('core', 'Закрыть'),
                        }
                        return JResponse(data)

                data = {
                    'response': 'ok',
                }
                return JResponse(data)

            else:
                data = {
                    'response': pgettext('new_player', 'Ошибка в форме профиля'),
                    'header': pgettext('new_player', 'Новый персонаж'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        # Если же это первый запрос к странице:
        nickname = ''
        if SocialAccount.objects.filter(user=request.user, provider='vk').exists():
            account = SocialAccount.objects.filter(user=request.user, provider='vk')[0]
            nickname = account.extra_data['first_name'] + ' ' + account.extra_data['last_name']

        elif SocialAccount.objects.filter(user=request.user, provider='google').exists():
            account = SocialAccount.objects.filter(user=request.user, provider='google')[0]
            nickname = account.extra_data['name']

        groups = list(request.user.groups.all().values_list('name', flat=True))
        page = 'player/redesign/new_player.html'

        return render(request, page, {'timezones': common,
                                      'default': default,
                                      'nickname': nickname,
                                      })
