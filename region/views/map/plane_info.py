import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import pgettext
from time import gmtime
from time import strftime
from player.decorators.player import check_player
from player.player import Player
from region.models.plane import Plane


@check_player
def plane_info(request, id):
    if request.method == "GET":
        if Player.objects.filter(pk=id).exists():
            player = Player.get_instance(pk=id)

            plane = None

            if Plane.objects.filter(in_use=True, player=player).exists():
                plane = Plane.objects.get(in_use=True, player=player)

            page = 'region/redesign/plane_info.html'
            return render(request, page, {
                'player': player,
                'plane': plane,
            })

        else:
            data = {
                'response': pgettext('plane_info', 'Игрок не существует'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'header': pgettext('plane_info', 'Информация о самолёте'),
            }
            return JsonResponse(data)
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'header': pgettext('plane_info', 'Информация о самолёте'),
        }
        return JsonResponse(data)
