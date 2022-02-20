from django.contrib.auth.decorators import login_required
from django.db import transaction

from chat.models.sticker_pack import StickerPack
from chat.models.stickers_ownership import StickersOwnership
from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from wild_politics.settings import JResponse


# покупка стикерпака
@login_required(login_url='/')
@check_player
@transaction.atomic
def buy_sticker_pack(request):
    if request.method == "POST":
        try:
            pack_id = int(request.POST.get('pack_id'))

        except ValueError:
            return {
                'header': 'Новый стикерпак',
                'grey_btn': 'Закрыть',
                'response': 'ID стикерпака должен быть целым числом',
            }

        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        if not StickerPack.actual.filter(pk=pack_id).exists():
            data = {
                'response': 'Указанный набор стикеров не найден',
                'header': 'Новый стикерпак',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # получаем стикерпак
        pack = StickerPack.actual.get(pk=pack_id)

        if player.gold < pack.price:
            data = {
                'response': 'Недостаточно золота, необходимо: ' + str(pack.price),
                'header': 'Новый стикерпак',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if StickersOwnership.objects.filter(owner=player, pack=pack).exists():
            data = {
                'response': 'У вас уже есть данный набор',
                'header': 'Новый стикерпак',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        player.gold -= pack.price

        gold_log = GoldLog(player=player, gold=0 - pack.price, activity_txt='stick')
        gold_log.save()

        player.save()

        new_entry = StickersOwnership(owner=player,
                                      pack=pack)
        new_entry.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Новый стикерпак',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
