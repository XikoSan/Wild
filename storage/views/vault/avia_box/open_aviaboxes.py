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


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
def open_aviaboxes(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        mode = request.POST.get('mode')

        if mode == 'rerun':
            if not LootboxPrize.objects.filter(player=player, deleted=False).exists():
                data = {
                    'response': 'У вас нет неполученных наград',
                    'header': 'Открытие Аэрокейсов',
                    'grey_btn': _('Закрыть'),
                }
                return JResponse(data)

            if player.gold < 500:
                data = {
                    'response': 'Недостаточно золота, необходимо: ' + str(500),
                    'header': 'Открытие Аэрокейсов',
                    'grey_btn': _('Закрыть'),
                }
                return JResponse(data)

            player.gold -= 500
            player.save()

            # находим последний выбитый приз, удаляем его. Отмечаем,что его заменили
            prize = LootboxPrize.objects.filter(player=player, deleted=False).order_by('-pk').first()
            prize.replaced = True
            prize.deleted = True
            prize.save()


        if LootboxPrize.objects.filter(player=player, deleted=False).exists():
            for prize in LootboxPrize.objects.filter(player=player, deleted=False):
                if not Plane.objects.filter(player=player, plane=prize.plane, color=prize.color).exists():
                    plane = Plane(player=player, plane=prize.plane, color=prize.color)
                    plane.save()

            LootboxPrize.objects.filter(player=player, deleted=False).update(deleted=True)

        if not mode == 'rerun' \
                and not Lootbox.objects.filter(player=player, stock__gt=0).exists():
            data = {
                'response': 'У вас нет Аэрокейсов',
                'header': 'Открытие Аэрокейсов',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        try:
            open_count = int(request.POST.get('count'))

        except ValueError:
            data = {
                'response': 'Некорректное количество Аэрокейсов для открытия',
                'header': 'Открытие Аэрокейсов',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        lootboxes = Lootbox.objects.get(player=player)

        if open_count > lootboxes.stock:
            data = {
                'response': 'Недостаточно Аэрокейсов для открытия',
                'header': 'Открытие Аэрокейсов',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)

        prizes = []

        GoldLog = apps.get_model('player.GoldLog')

        loop = 0
        for box in range(open_count):

            if lootboxes.garant_in == 0:
                reward, type = generate_rewards(player, True)

            else:
                reward, type = generate_rewards(player)

            if type == 'epic':
                lootboxes.garant_in = 100

            else:
                lootboxes.garant_in -= 1


            if type == 'gold':
                player.gold += reward

                prizes.append([[type, reward], f'{number_format(reward)} золота' ,'валюта'])

                gold_log = GoldLog(player=player, gold=reward, activity_txt='bx_gld')
                gold_log.save()

                player.save()

            else:
                reward_color = 'базовый'
                for tuple in Plane.colorChoices:
                    if reward[1] == tuple[0]:
                        reward_color = tuple[1]
                        break

                plane_name = 'самолёт'
                for tuple in Plane.planesChoices:
                    if reward[0] == tuple[0]:
                        if tuple[0] == 'beluzzo':
                            plane_name = f'{tuple[1]}'
                        else:
                            plane_name = f'{tuple[1]} {reward_color}'
                        break

                rarity = 'обычный'

                if type == 'epic':
                    rarity = 'уникальный'
                if type == 'rare':
                    rarity = 'особый'

                prize = LootboxPrize(player=player, plane=reward[0], color=reward[1])
                prize.save()

                prizes.append([reward, plane_name, rarity])

        if not mode == 'rerun':
            lootboxes.stock -= open_count
        lootboxes.save()

        data = {
            'response': 'ok',
            'prizes': prizes,

            'boxes_count': lootboxes.stock,
            'garant_count': lootboxes.garant_in,
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
