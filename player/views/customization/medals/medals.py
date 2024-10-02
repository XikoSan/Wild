from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.models.medal import Medal
from player.player import Player


@login_required(login_url='/')
@check_player
# открытие страницы наград
def view_medals(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if pk != player.pk:
        # Пользователб, чью страницу необходимо просмотреть
        char = get_object_or_404(Player, pk=pk)
    else:
        char = player

    medals = None

    types_list = []

    for type in Medal.medalTypeChoices:
        types_list.append(type[0])

    exists_dict = {}

    medals = Medal.objects.filter(player=char)

    for type in types_list:
        if medals and medals.filter(type=type).exists():
            exists_dict[type] = medals.get(type=type).count
        else:
            exists_dict[type] = None


    return render(request, 'player/redesign/customization/view_medals.html', {
        'page_name': pgettext('medals', 'Награды'),
        'player': player,
        'char': char,

        'types_list': types_list,
        'exists_dict': exists_dict,
        'medals': medals,
    })
