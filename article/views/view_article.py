import json
import os
import redis
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain
import datetime
import random
from chat.models.sticker import Sticker
import pytz
from article.models.article import Article
from article.models.subscription import Subscription
from chat.models.stickers_ownership import StickersOwnership
from player.decorators.player import check_player
from player.player import Player
from django.utils import timezone


# открыть статью
@login_required(login_url='/')
@check_player
def view_article(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    voted = None
    subscription = False
    comments = True

    if Article.objects.filter(pk=pk).exists():
        article = Article.objects.get(pk=pk)

        if article.date < timezone.now() - datetime.timedelta(days=1):
            comments = False

        if player in article.votes_pro.all():
            voted = 'pro'
        elif player in article.votes_con.all():
            voted = 'con'

        if Subscription.objects.filter(
                author=article.player,
                player=player
        ).exists():
            subscription = True

    else:
        # перекидываем в список статей
        return redirect("articles")

    http_use = False
    if os.getenv('HTTP_USE'):
        http_use = True

    messages = []

    stickers_dict = {}
    stickers_header_dict = {}
    header_img_dict = {}

    r = None

    if not player.chat_ban and comments:
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        counter = 0

        if r.hlen(f'counter_{article.pk}') > 0:
            counter = r.hget(f'counter_{article.pk}', 'counter')

        redis_list = r.zrangebyscore(f'comments_{article.pk}', 0, counter, withscores=True)

        for scan in redis_list:
            b = json.loads(scan[0])

            if not Player.objects.filter(pk=int(b['author'])).exists():
                r.zremrangebyscore(f'comments_{article.pk}', int(scan[1]), int(scan[1]))
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
                b['image_link'] = author.image.url
            else:
                b['image_link'] = 'nopic'

            b['user_pic'] = False
            # если сообщение - ссылка на изображение
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            if any(extension in b['content'].lower() for extension in image_extensions):
                b['user_pic'] = True

            messages.append(b)

        stickers = StickersOwnership.objects.filter(owner=player)

        for sticker_own in stickers:
            # название пака
            stickers_header_dict[sticker_own.pack.pk] = sticker_own.pack.title
            #  получим рандомную картинку для заголовка
            header_img_dict[sticker_own.pack.pk] = random.choice(
                Sticker.objects.filter(pack=sticker_own.pack)).image.url
            # все остальные картинки - в словарь
            stickers_dict[sticker_own.pack.pk] = Sticker.objects.filter(pack=sticker_own.pack)

    # отправляем в форму
    return render(request, 'article/article.html', {
        'page_name': article.title,
        # самого игрока
        'player': player,
        # статья
        'article': article,

        # рейтинг статьи
        'article_rating': article.votes_pro.count() - article.votes_con.count(),
        'article_rated_up': article.votes_pro.count(),
        'article_rated_down': article.votes_con.count(),

        # голосовал ли
        'voted': voted,
        # подписан ли
        'subscription': subscription,

        # комментарии выключены (прошли сутки)
        'comments': comments,

        # комментарии
        'messages': messages,

        'stickers_header_dict': stickers_header_dict,
        'header_img_dict': header_img_dict,
        'stickers_dict': stickers_dict,

        'http_use': http_use,
    })
