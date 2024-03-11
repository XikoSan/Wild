# coding=utf-8
import json
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import ugettext

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from region.models.neighbours import Neighbours
from region.models.region import Region
from storage.models.storage import Storage
from wild_politics.settings import JResponse


# сохранить список связей регионов
@login_required(login_url='/')
@check_player
@transaction.atomic
def save_links(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if not player.account.is_superuser:
            data = {
                'response': pgettext('mining', 'нет полномочий'),
                'header': pgettext('mining', 'связи регионов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        links_list = json.loads(request.POST.get('links'))

        all_regions = Region.objects.all()

        for link in links_list:

            if not Neighbours.objects.filter(
                    Q(region_1=all_regions.get(on_map_id=link[0]), region_2=all_regions.get(on_map_id=link[1]))
                    | Q(region_2=all_regions.get(on_map_id=link[0]), region_1=all_regions.get(on_map_id=link[1]))
            ).exists():
                neig = Neighbours(
                    region_1=all_regions.get(on_map_id=link[0]),
                    region_2=all_regions.get(on_map_id=link[1]),
                )
                neig.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': pgettext('mining', 'Ошибка автоматической добычи ресурсов'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': ugettext('Ошибка метода'),

        }
        return JResponse(data)
