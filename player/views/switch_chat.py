from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
import redis
import pytz
import json
import datetime
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
from django.shortcuts import render


# переключение между чатами
@login_required(login_url='/')
@check_player
def switch_chat(request, chat_id):
    if request.method == "GET":

        messages = []

        player = Player.get_instance(account=request.user)

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        appendix = ''

        if chat_id != 'ru':
            # appendix = f'_{chat_id}'
            appendix = f'_en'

        counter = 0

        if r.hlen('counter' + appendix) > 0:
            counter = r.hget('counter' + appendix, 'counter')

        redis_list = r.zrangebyscore("chat" + appendix, 0, counter, withscores=True)

        for scan in redis_list:
            b = json.loads(scan[0])

            if not Player.objects.filter(pk=int(b['author'])).exists():
                r.zremrangebyscore('chat' + appendix, int(scan[1]), int(scan[1]))
                continue

            author = Player.objects.filter(pk=int(b['author'])).only('id', 'nickname', 'image', 'time_zone').get()
            # сначала делаем из наивного времени aware, потом задаем ЧП игрока
            b['dtime'] = datetime.datetime.fromtimestamp(int(b['dtime'])).astimezone(
                tz=pytz.timezone(player.time_zone)).strftime("%H:%M")
            b['author'] = author.pk
            b['counter'] = int(scan[1])

            if len(author.nickname) > 25:
                b['author_nickname'] = f'{author.nickname[:25]}...'
            else:
                b['author_nickname'] = author.nickname

            if author.image:
                b['image_link'] = author.image_75.url
            else:
                b['image_link'] = 'nopic'

            b['user_pic'] = False
            # если сообщение - ссылка на изображение
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            if any(extension in b['content'].lower() for extension in image_extensions):
                b['user_pic'] = True

            messages.append(b)

        page = 'player/redesign/switch_chat.html'

        return render(request, page, {
            'player': player,
            'messages': messages,
        })


    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('chat', 'Новый стикерпак'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JsonResponse(data)