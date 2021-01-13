from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from player.player import Player
from storage.models.storage import Storage


# Производство
def get_storage_action_line(request, type):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    storage = Storage.objects.get(owner=player, region=player.region)

    return render(request, 'storage/storage_lines/' + type + '.html', {'player': player,
                                                                       'storage': storage,
                                                                       })
