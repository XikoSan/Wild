import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.player_settings import PlayerSettings
from storage.views.vault.avia_box.generate_rewards import generate_rewards
from wild_politics.settings import JResponse
from django.contrib.humanize.templatetags.humanize import number_format
from region.models.plane import Plane
from storage.models.lootbox_prize import LootboxPrize


# За лутбоксы
@login_required(login_url='/')
@check_player
def loot_aviaboxes(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        import redis
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        if LootboxPrize.objects.filter(player=player, deleted=False).exists():
            for prize in LootboxPrize.objects.filter(player=player, deleted=False):
                if not Plane.objects.filter(player=player, plane=prize.plane, color=prize.color).exists():
                    plane = Plane(player=player, plane=prize.plane, color=prize.color)
                    plane.save()

                    if r.exists(f"{player.pk}_planes_count"):
                        r.set(f"{player.pk}_planes_count", int(r.get(f"{player.pk}_planes_count")) + 1)
                    else:
                        r.set(f"{player.pk}_planes_count", 1)

            LootboxPrize.objects.filter(player=player).update(deleted=True)

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': _('Открытие Аэрокейсов'),
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
