from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.good import Good


@login_required(login_url='/')
@check_player
# открытие страницы аукционов
def auctions(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    goods_by_types = {}
    goods = Good.objects.all()

    for good in goods:
        if good.type in goods_by_types:
            goods_by_types[good.type].append(good)
        else:
            goods_by_types[good.type] = [good]

    types_texts = {}
    for type in Good.typeChoices:
        types_texts[type[0]] = type[1]

    return render(request, 'storage/redesign/auctions/auctions.html', {'player': player,
                                                                    'storage_cl': Storage,
                                                                    'transport': Transport,

                                                                    'goods': goods,
                                                                    'goods_by_types': goods_by_types,
                                                                    'types_texts': types_texts,
                                                                })
