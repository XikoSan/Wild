import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.models.sticker import Sticker
from chat.models.sticker_pack import StickerPack
from chat.models.stickers_ownership import StickersOwnership
from player.decorators.player import check_player
from player.player import Player


@login_required(login_url='/')
@check_player
# открытие страницы кошелька игрока
def stickers_shop(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    # получаем стикерпаки в собственности
    my_packs = StickersOwnership.objects.filter(owner=player)

    # получаем сами паки из записей владения
    my_packs_pk_list = []
    for pack_own in my_packs:
        my_packs_pk_list.append(pack_own.pack.pk)

    # получаем все стикерпаки, кроме имеющихся
    available_packs = StickerPack.actual.exclude(pk__in=my_packs_pk_list)

    # получаем все стикеры доступных стикерпаков
    available_stickers = Sticker.actual.filter(pack__in=available_packs)

    stickers_dict = {}
    header_img_dict = {}

    for pack in available_packs:
        #  получим рандомную картинку для заголовка
        header_img_dict[pack.pk] = random.choice(available_stickers.filter(pack=pack)).image.url
        # все остальные картинки - в словарь
        stickers_dict[pack.pk] = available_stickers.filter(pack=pack)


    return render(request, 'chat/sticker-shop.html', {'player': player,
                                                       'page_name': 'Магазин стикеров',

                                                       'available_packs': available_packs,
                                                       'header_img_dict': header_img_dict,

                                                       'stickers_dict': stickers_dict,
                                                       })
