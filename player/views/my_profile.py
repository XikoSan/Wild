import pytz
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from player.player import Player
from player.decorators.player import check_player


@login_required(login_url='/')
@check_player
# открытие страницы персонажа игрока
def my_profile(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    player_settings = None

    # timezones = pytz.common_timezones
    #
    # if PlayerSettings.objects.filter(player=player).exists():
    #     player_settings = PlayerSettings.objects.get(player=player)

    # ---------------------
    # cursor = connection.cursor()
    # cursor.execute("SELECT COUNT(DISTINCT store.cash + player.cash) FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE store.cash + player.cash >= (SELECT store.cash + player.cash FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE player.id=%s LIMIT 1);", [player.pk])
    # cash_rating = cursor.fetchone()
    # ---------------------

    return render(request, 'player/profile.html', {'player': player,
                                                   # 'timezones': timezones,
                                                   # 'cash_rating': cash_rating[0],
                                                   # 'player_settings': player_settings,
                                                   # 'countdown': UntilRecharge(player)
                                                   })

    #
    # @login_required(login_url='/')
    # @check_player
    # # Открытие страницы просмотра профиля персонажа
    # def ProfileToView(request, pk):
    #     # Получаем объект персонажа, по его ключу
    #     # Текущий пользователь
    #     player = Player.objects.get(account=request.user)
    #     # Пользователб, чью страницу необходимо просмотреть
    #     char = get_object_or_404(Player, pk=pk)
    #     # если игрок хочет посмотреть самого себя
    #     if player == char:
    #         # перекидываем его в профиль
    #         return redirect("my_profile")
    #     char_settings = None
    #     if PlayerSettings.objects.filter(player=char).exists():
    #         char_settings = PlayerSettings.objects.get(player=char)
    #     # ---------------------
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT COUNT(DISTINCT store.cash + player.cash) FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE store.cash + player.cash >= (SELECT store.cash + player.cash FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE player.id=%s LIMIT 1);", [char.pk])
    #     cash_rating = cursor.fetchone()
    #     # ---------------------
    #     return render(request, 'gamecore/main_menu/Profile/ProfileToView.html', {'player': player,
    #                                                                              'char': char,
    #                                                                              'cash_rating': cash_rating[0],
    # 'char_settings': char_settings,
    # 'countdown': UntilRecharge(player)})
