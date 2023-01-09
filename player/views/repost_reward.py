from datetime import datetime, timedelta

import pytz
import vk
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from wild_politics.settings import JResponse
from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from wild_politics.settings import TIME_ZONE


# Начать учет активности
@login_required(login_url='/')
@check_player
def repost_reward(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # ====== API VK =====
        repost = False
        timer = False
        need_dtime = None

        if SocialToken.objects.filter(account__user=player.account, account__provider='vk').exists():
            session = vk.Session(
                access_token=SocialToken.objects.get(account__user=player.account, account__provider='vk'))
            vk_api = vk.API(session)

            response = vk_api.wall.get(owner_id=SocialAccount.objects.filter(user=player.account, provider='vk')[0].uid,
                                       v='5.131', count=2)

            for item in response.get('items'):

                if 'copy_history' in item \
                        and item['copy_history'][0]['owner_id'] == -164930433 \
                        and item['copy_history'][0]['id'] == 4379:
                    repost = True
                    # берем TIMESTAMP из ВК, приводим его к часовому поясу сервера, потом - к поясу игрока и прибавляем час
                    need_dtime = datetime.fromtimestamp(item['date'], tz=pytz.timezone(TIME_ZONE)).astimezone(
                        pytz.timezone(player.time_zone)) + timedelta(hours=1)
                    if timezone.now().astimezone(pytz.timezone(player.time_zone)) > need_dtime:
                        timer = True

            if not repost:
                data = {
                    'response': 'Репост не найден',
                    'header': 'Ошибка бонуса за репост',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            if not timer:
                data = {
                    'response': 'Час после репоста ещё не прошёл',
                    'header': 'Ошибка бонуса за репост',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            if GoldLog.objects.filter(player=player, dtime__gte=timezone.now() - timedelta(days=1),
                                      activity_txt='reward').exists():
                new_reward_date = GoldLog.objects.get(player=player, dtime__gte=timezone.now() - timedelta(days=1),
                                                      activity_txt='reward').dtime + timedelta(days=1)
                new_reward_date = new_reward_date.astimezone(pytz.timezone(player.time_zone)).strftime('%Y-%m-%d %H:%M')
                data = {
                    'response': 'Сутки после предыдущего бонуса ещё не прошли.\nПодождите до ' + new_reward_date,
                    'header': 'Ошибка бонуса за репост',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            gold_log = GoldLog(player=player, gold=250, activity_txt='reward')
            gold_log.save()
            Player.objects.filter(pk=player.pk).update(gold=F('gold') + 250)

            data = {
                'response': 'ok',
            }
            return JsonResponse(data)

        else:
            data = {
                'response': 'Персонаж не связан с ВК',
                'header': 'Ошибка бонуса за репост',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка метода',
            'header': 'Ошибка бонуса за репост',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
