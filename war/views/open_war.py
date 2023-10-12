

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player

from war.models.wars.war import War
from django.db.models import Sum
from django.db.models import F


# страница войн
@login_required(login_url='/')
@check_player
def open_war(request, class_name, pk):
    try:
        war_class = apps.get_model('war', class_name)

    except KeyError:
        return redirect('war_page')

    if not war_class.objects.filter(pk=pk).exists():
        return redirect('war_page')

    war = war_class.objects.get(pk=pk)

    # отправляем класс войны
    return war.get_page(request)
