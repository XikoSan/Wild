import datetime
import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from war.models.martial import Martial
from war.models.wars.revolution.rebel import Rebel
from war.models.wars.revolution.revolution import Revolution
from wild_politics.settings import JResponse


# запуск войны в текущем регионе
@login_required(login_url='/')
@check_player
@transaction.atomic
def join_revolution(request):
    if request.method == "POST":

        # получаем персонажа
        player = Player.get_instance(account=request.user)

        price = 500
        resident = False

        if Martial.objects.filter(active=True, region=player.region).exists():
            if player.region == player.residency:
                price = 100
                resident = True
            else:
                price = 300
        else:
            if player.region == player.residency:
                price = 300
                resident = True

        # проверяем наличие голды
        if player.gold < price:
            data = {
                'response': 'Недостаточно золота',
                'header': 'Участие в восстании',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if Rebel.actual.filter(region=player.region).count() == 2 \
                and Revolution.objects.filter(
            agr_region=player.region,
            def_region=player.region,
            end_time__gt=timezone.now() - datetime.timedelta(days=7)
        ).exists():
            data = {
                'response': 'С момента завершения последнего восстания не прошло 7 дней',
                'header': 'Участие в восстании',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # если есть два повстанца без прописки и ни одного с ней
        if Rebel.actual.filter(region=player.region, resident=False).count() == 2 \
                and not Rebel.actual.filter(region=player.region, resident=True).exists():

            if not player.region == player.residency:
                data = {
                    'response': 'Для участия в восстании требуется прописка',
                    'header': 'Участие в восстании',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

        if Rebel.actual.filter(
                player=player,
                region=player.region
        ).exists():
            data = {
                'response': 'Вы уже являетесь участником восстания здесь',
                'header': 'Участие в восстании',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # если с момента последнего участия в восстании прошло менее десяти дней
        if Rebel.objects.filter(
                player=player,
                dtime__gt=timezone.now() - datetime.timedelta(days=10)
        ).exists():
            data = {
                'response': 'Вы принимали участие в восстании последние 10 дней',
                'header': 'Участие в восстании',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        rebel = Rebel(
            region=player.region,
            player=player,
            resident=resident
        )

        player.gold -= price

        gold_log = GoldLog(player=player, gold=-price, activity_txt='rebel')
        gold_log.save()

        player.save()
        rebel.save()

        if Rebel.actual.filter(region=player.region).count() >= 3:
            new_war = Revolution(
                running=True,
                agr_region=player.region,
                def_region=player.region,
            )

            new_war.save()

            Rebel.actual.filter(region=player.region).update(deleted=True)

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Участие в восстании',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
