import pytz
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from PIL import Image
from player.logs.gold_log import GoldLog
from django.core.files import File
from player.player import Player
from player.decorators.player import check_player
from player.forms import ImageForm
from allauth.socialaccount.models import SocialAccount


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
            resized_image.save(player.image.path)
            
            return redirect('my_profile')
    else:
        form = ImageForm()

    user_link = ''

    if SocialAccount.objects.filter(user=player.account).exists():
        if SocialAccount.objects.filter(user=player.account).all()[0].provider == 'vk':
            user_link = 'https://vk.com/id' + SocialAccount.objects.filter(user=player.account).all()[0].uid

    # timezones = pytz.common_timezones
    #
    # if PlayerSettings.objects.filter(player=player).exists():
    #     player_settings = PlayerSettings.objects.get(player=player)

    # ---------------------
    # cursor = connection.cursor()
    # cursor.execute("SELECT COUNT(DISTINCT store.cash + player.cash) FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE store.cash + player.cash >= (SELECT store.cash + player.cash FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE player.id=%s LIMIT 1);", [player.pk])
    # cash_rating = cursor.fetchone()
    # ---------------------

    return render(request, 'player/profile.html', {'player': player,
                                                   'form': form,

                                                   'user_link': user_link,
                                                   # 'timezones': timezones,
                                                   # 'cash_rating': cash_rating[0],
                                                   # 'player_settings': player_settings,
                                                   # 'countdown': UntilRecharge(player)
                                                   'page_name': player.nickname,
                                                   })
