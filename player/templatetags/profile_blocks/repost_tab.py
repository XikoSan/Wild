import pytz
import vk
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken
from datetime import datetime, timedelta
from django import template
from django.utils import timezone
from wild_politics.settings import TIME_ZONE
register = template.Library()


@register.inclusion_tag('player/player_repost.html')
def repost_tab(player):
    # ====== API VK =====
    repost = False
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
                    and item['copy_history'][0]['id'] == 2117:
                repost = True
                # берем TIMESTAMP из ВК, приводим его к часовому поясу сервера, потом - к поясу игрока и прибавляем час
                need_dtime = datetime.fromtimestamp(item['date'], tz=pytz.timezone(TIME_ZONE)).astimezone(pytz.timezone(player.time_zone)) + timedelta(hours=1)

        return {
            # игрок
            'player': player,
            'need_dtime': need_dtime,
            'now_dtime': timezone.now().astimezone(pytz.timezone(player.time_zone)),
            'repost': repost,
        }

