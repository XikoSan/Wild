# coding=utf-8
import pytz
import random
from django.contrib.auth.decorators import login_required
# from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

# from django.utils.translation import ugettext as _
#
from player.forms import NewPlayerForm
# from gamecore.all_models.mail import Message
# from gamecore.all_models.player import Player, Partners
from player.player import Player
from region.region import Region
# from gamecore.all_models.storage import Storage
from storage.storage import Storage


# Функция создания нового персонажа
def player_create(request, form):
    # Создаем нового игрока
    character = form.save(commit=False)
    character.account = request.user
    character.save()

    # settings = PlayerSettings(player=character)
    #     # settings.save()

    start_pk = random.choice(Region.objects.all())
    # Помещаем нового персонажа в случаный регион и прописываем там же
    character.region = start_pk
    character.residency = start_pk

    storage = Storage(owner=character, region=character.region)
    storage.save()

    # mess = Message(player_from=Player.objects.get(pk=1), player_to=character, body=_(
    #     'Welcome! I am the creator and administrator of this game. This message was created automatically - but you can reply to me, ask your question right here, or by contacting me through VK/Discord. I highly recommend reading the “First Steps” article on the Wiki, and joining one of the parties in your state’s parliament. If you have any difficulties with the game or with team finding - write to me, I will help. Also, I will be glad to feedback. Have a nice game!'),
    #                new=True)
    # mess.save()

    return character


# новый персонаж
@login_required(login_url='/')
def new_player(request):
    # если у игрока есть хоть один персонаж:
    if Player.objects.filter(account=request.user).exists():
        # возврат в главное меню
        return redirect('overview')
    else:
        # Если форма нового персонажа возвращена заполненной
        common = pytz.common_timezones
        # the name of the default time zone
        default = timezone.get_default_timezone_name()
        if request.method == "POST":
            form = NewPlayerForm(request.POST, request.FILES)
            # если форма заполненна корректно
            if form.is_valid():
                # Создаем его персонажа и перенаправляем в Overview
                character = player_create(request, form)
                character.save()
                data = {
                    'response': 'ok',
                }
                return JsonResponse(data)
            else:
                return render(request, 'player/new_player.html', {'timezones': common,
                                                                  'default': default,
                                                                  'not_valid': 'True'})
            # Если же это первый запрос к странице:
        else:
            pass
        return render(request, 'player/new_player.html', {'timezones': common, 'default': default, })
