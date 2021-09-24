from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.core.serializers import serialize
from player.decorators.player import check_player
from player.player import Player
from chat.models import Chat, Message
import json
import redis
from django.templatetags.static import static
from player.logs.print_log import log
from django.utils import timezone
from datetime import datetime
from wild_politics.settings import TIME_ZONE
import pytz

# главная страница
@login_required(login_url='/')
@check_player
def overview(request):
    player = Player.objects.get(account=request.user)

    messages = []

    if not player.chat_ban:
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        counter = 0

        if r.hlen('counter') > 0:
            counter = r.hget('counter', 'counter')

        redis_list = r.zrangebyscore("chat", 0, counter)

        for scan in redis_list:
            b = json.loads(scan)
            author = Player.objects.filter(pk=int(b['author'])).only('id', 'image', 'time_zone').get()
            # сначала делаем из наивного времени aware, потом задаем ЧП игрока
            b['dtime'] = datetime.fromtimestamp(int(b['dtime'])).replace(tzinfo=pytz.timezone(TIME_ZONE)).astimezone(tz=pytz.timezone(player.time_zone)).strftime("%H:%M")
            b['author'] = author.pk
            if author.image:
                b['image_link'] = author.image.url
            else:
                b['image_link'] = static('img/nopic.png')
            messages.append(b)


    # отправляем в форму
    response = render(request, 'player/overview.html', {
        'page_name': _('Обзор'),

        'player': player,

        'messages': messages,

    })

    # r.flushdb()

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
