import pytz
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from allauth.socialaccount.models import SocialAccount
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Sum
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from article.models.article import Article
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.forms import ImageForm
from player.logs.gold_log import GoldLog
from player.player import Player
from player.player_settings import PlayerSettings
from region.models.plane import Plane
from war.models.wars.player_damage import PlayerDamage
from player.logs.test_log import TestLog


@login_required(login_url='/')
@check_player
# открытие страницы персонажа игрока
def my_profile(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    player_settings = None

    # from player.logs.print_log import log
    #
    # if request.method == 'POST':
    #     if player.image and player.gold < 100:
    #         log("Недостаточно золота для изменения аватара.")
    #         return redirect('my_profile')
    #
    #     form = ImageForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         try:
    #             # Не списывать деньги, если аватара нет
    #             if player.image:
    #                 player.gold -= 100
    #                 gold_log = GoldLog(player=player, gold=-100, activity_txt='avatar')
    #                 gold_log.save()
    #                 log(f"Списано 100 золота. Остаток золота: {player.gold}")
    #
    #             # Загружаем и подготавливаем изображение
    #             player.image = form.cleaned_data['image']
    #             player.save()  # Сохраняем игрока с новым изображением, чтобы обновить путь
    #             log("Аватар успешно сохранен в профиле игрока.")
    #
    #             x = form.cleaned_data['x']
    #             y = form.cleaned_data['y']
    #             w = form.cleaned_data['width']
    #             h = form.cleaned_data['height']
    #
    #             try:
    #                 # Открываем загруженное изображение и обрезаем
    #                 image = Image.open(player.image.path)
    #                 cropped_image = image.crop((x, y, w + x, h + y))
    #                 resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)
    #                 log("Изображение обрезано и изменено до 400x400.")
    #             except Exception as e:
    #                 log(f"Ошибка при обработке изображения: {e}")
    #                 return redirect('my_profile')
    #
    #             try:
    #                 # Устанавливаем путь для основного изображения и сохраняем
    #                 webp_image_path = f'img/avatars/{player.id}.webp'
    #                 resized_image.save(player.image.storage.path(webp_image_path), 'WEBP', quality=85)
    #                 player.image.name = webp_image_path
    #                 player.save()
    #                 log(f"Основное изображение сохранено и путь обновлён: {webp_image_path}.")
    #             except Exception as e:
    #                 log(f"Ошибка при сохранении основного изображения: {e}")
    #                 return redirect('my_profile')
    #
    #             try:
    #                 # Создаем уменьшенные изображения
    #                 # Сохраняем 75x75 в img/avatars/75/
    #                 image_75 = resized_image.resize((75, 75), Image.ANTIALIAS)
    #                 img_io_75 = BytesIO()
    #                 image_75.save(img_io_75, format='WEBP', quality=85)
    #                 player.image_75.save(f"{player.id}.webp", ContentFile(img_io_75.getvalue()), save=False)
    #                 log("Изображение 75x75 сохранено.")
    #
    #                 # Сохраняем 33x33 в img/avatars/33/
    #                 image_33 = resized_image.resize((33, 33), Image.ANTIALIAS)
    #                 img_io_33 = BytesIO()
    #                 image_33.save(img_io_33, format='WEBP', quality=85)
    #                 player.image_33.save(f"{player.id}.webp", ContentFile(img_io_33.getvalue()), save=False)
    #                 log("Изображение 33x33 сохранено.")
    #
    #                 # Сохраняем изменения в модели игрока
    #                 player.save()
    #                 log("Изменения в модели игрока успешно сохранены.")
    #             except Exception as e:
    #                 log(f"Ошибка при сохранении уменьшенных изображений: {e}")
    #                 return redirect('my_profile')
    #
    #         except Exception as e:
    #             log(f"Ошибка при обработке запроса POST: {e}")
    #             return redirect('my_profile')
    #     else:
    #         log("Форма недействительна.")
    # else:
    form = ImageForm()

    user_link = ''

    if SocialAccount.objects.filter(user=player.account).exists():
        if SocialAccount.objects.filter(user=player.account).all()[0].provider == 'vk':
            user_link = 'https://vk.com/id' + SocialAccount.objects.filter(user=player.account).all()[0].uid

    premium = None
    if player.premium > timezone.now():
        premium = player.premium

    minister = None
    if Minister.objects.filter(player=player).exists():
        minister = Minister.objects.get(player=player)

    #  Настройки цветов профиля
    setts = None

    color_back = '28353E'
    color_block = '284E64'
    color_text = 'FFFFFF'
    color_acct = 'EB9929'

    party_back = True
    full_auto = False
    wiki_hide = False

    if PlayerSettings.objects.filter(player=player).exists():
        setts = PlayerSettings.objects.get(player=player)

        color_back = setts.color_back
        color_block = setts.color_block
        color_text = setts.color_text
        color_acct = setts.color_acct

        party_back = setts.party_back
        full_auto = setts.full_auto
        wiki_hide = setts.wiki_hide

    ava_border = None
    png_use = False
    if AvaBorderOwnership.objects.filter(in_use=True, owner=player).exists():
        border = AvaBorderOwnership.objects.get(in_use=True, owner=player)

        ava_border = border.border
        png_use = border.png_use

    # ---------------------
    cursor = connection.cursor()

    # ============================ селект, выводящий место игрока в рейтинге по деньгам
    # with sum_limit(lim) as
    #     (
    #         select SUM(store.cash) + player.cash
    #     from player_player as player
    #     join storage_storage as store
    #     on player.id = 68
    #                 and store.owner_id = player.id
    #                                      and store.deleted = false
    #     group
    #     by
    #     player.id
    #     ),
    #
    #     store_sum(owner_id, cash) as
    #     (
    #         select store.owner_id, sum(store.cash)
    #     from storage_storage as store
    #     where
    #     store.deleted = false
    #     group
    #     by
    #     store.owner_id
    #     )
    #
    #     select
    #     count(*) + 1
    #     from player_player as player
    #
    #     join
    #     store_sum as store
    #     on
    #     store.owner_id = player.id
    #
    #     where
    #     store.cash + player.cash > (select lim from sum_limit);

    cursor.execute(
        "with sum_limit (lim) as ( select SUM(store.cash) + player.cash from player_player as player join storage_storage as store on player.id = %s and store.owner_id = player.id and store.deleted = false group by player.id ), store_sum (owner_id, cash) as ( select store.owner_id, sum(store.cash) from storage_storage as store where store.deleted = false group by store.owner_id ) select count ( * ) + 1 from player_player as player join store_sum as store on store.owner_id = player.id where store.cash + player.cash > ( select lim from sum_limit );",
        [player.pk])
    cash_rating = cursor.fetchone()
    # ---------------------
    player_articles = Article.objects.only('pk').filter(player=player).values('pk')

    if player_articles:
        articles_tuple = ()

        for article in player_articles:
            articles_tuple += (article['pk'],)

        cursor.execute(
            "with lines_con as(select count(*) from public.article_article_votes_con where article_id in %s), lines_pro as (select count(*) from public.article_article_votes_pro where article_id in %s) SELECT lines_pro.count - lines_con.count AS difference FROM lines_con, lines_pro;",
            [articles_tuple, articles_tuple])

        carma = cursor.fetchall()[0][0]

    else:
        carma = 0
    # ---------------------

    dmg_sum = PlayerDamage.objects.filter(player=player).aggregate(dmg_sum=Sum('damage'))['dmg_sum']

    if not dmg_sum:
        dmg_sum = 0

    # ---------------------

    if Plane.objects.filter(in_use=True, player=player).exists():
        plane = Plane.objects.get(in_use=True, player=player)
        plane_url = f'/static/img/planes/{plane.plane}/{plane.plane}_{plane.color}.svg'
    else:
        plane_url = '/static/img/planes/nagger/nagger_base.svg'

    # ---------------------

    CashEvent = apps.get_model('event.CashEvent')

    inviting_event = CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                              event_end__gt=timezone.now()).exists()

    # ---------------------

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    test_points = None

    if "WildPoliticsApp" in user_agent:
        test_points = TestLog.objects.filter(player=player).count()

    # ---------------------

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'player/profile.html'
    if 'redesign' not in groups:
        page = 'player/redesign/profile.html'

    response = render(request, page, {
        'player': player,
        'form': form,

        'premium': premium,
        'minister': minister,

        'user_link': user_link,
        'cash_rating': cash_rating[0],
        'carma': carma,
        'dmg_sum': dmg_sum,
        # 'player_settings': player_settings,
        # 'countdown': UntilRecharge(player)
        'page_name': player.nickname,

        'timezones': pytz.common_timezones,

        'color_back': color_back,
        'color_block': color_block,
        'color_text': color_text,
        'color_acct': color_acct,

        'party_back': party_back,
        'full_auto': full_auto,
        'wiki_hide': wiki_hide,

        'ava_border': ava_border,
        'png_use': png_use,
        'plane_url': plane_url,

        'inviting_event': inviting_event,

        'test_points': test_points,

    })

    return response
