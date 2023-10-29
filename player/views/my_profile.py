import pytz
from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from gov.models.minister import Minister
from player.decorators.player import check_player
from player.forms import ImageForm
from player.logs.gold_log import GoldLog
from player.player import Player
from player.player_settings import PlayerSettings
from ava_border.models.ava_border_ownership import AvaBorderOwnership


@login_required(login_url='/')
@check_player
# открытие страницы персонажа игрока
def my_profile(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    player_settings = None

    if request.method == 'POST':
        if player.image and player.gold < 100:
            return redirect('my_profile')

        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # не списывать деньги, если аватара нет
            if player.image:
                player.gold -= 100

                gold_log = GoldLog(player=player, gold=-100, activity_txt='avatar')
                gold_log.save()

            player.image = form.cleaned_data['image']

            player.save()

            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            w = form.cleaned_data['width']
            h = form.cleaned_data['height']

            image = Image.open(player.image)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((250, 250), Image.ANTIALIAS)
            resized_image.save(player.image.path, 'PNG')

            return redirect('my_profile')
    else:
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
    if AvaBorderOwnership.objects.filter(in_use=True, owner=player).exists():
        ava_border = AvaBorderOwnership.objects.get(in_use=True, owner=player).border

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

    cursor.execute("with sum_limit (lim) as ( select SUM(store.cash) + player.cash from player_player as player join storage_storage as store on player.id = %s and store.owner_id = player.id and store.deleted = false group by player.id ), store_sum (owner_id, cash) as ( select store.owner_id, sum(store.cash) from storage_storage as store where store.deleted = false group by store.owner_id ) select count ( * ) + 1 from player_player as player join store_sum as store on store.owner_id = player.id where store.cash + player.cash > ( select lim from sum_limit );", [player.pk])
    cash_rating = cursor.fetchone()
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

    })
    return response
