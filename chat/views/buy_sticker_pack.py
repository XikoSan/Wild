from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import pgettext
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
            data = {
                'header': pgettext('chat', 'Новый стикерпак'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('chat', 'ID стикерпака должен быть целым числом'),
            }
            return JResponse(data)

        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        if not StickerPack.actual.filter(pk=pack_id).exists():
            data = {
                'response': pgettext('chat', 'Указанный набор стикеров не найден'),
                'header': pgettext('chat', 'Новый стикерпак'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # получаем стикерпак
        pack = StickerPack.actual.get(pk=pack_id)

        if player.gold < pack.price:
            data = {
                'response': pgettext('new_article', 'Недостаточно золота, необходимо: %(price)s') % { "price": pack.price },
                'header': pgettext('chat', 'Новый стикерпак'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if StickersOwnership.objects.filter(owner=player, pack=pack).exists():
            data = {
                'response': pgettext('chat', 'У вас уже есть данный набор'),
                'header': pgettext('chat', 'Новый стикерпак'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        player.gold -= pack.price

        gold_log = GoldLog(player=player, gold=0 - pack.price, activity_txt='stick')
        gold_log.save()

        player.save()

        new_entry = StickersOwnership(owner=player,
                                      pack=pack)
        new_entry.save()
        # если у пака есть выгодоприобретатель
        if pack.owner:
            owner = Player.get_instance(pk=pack.owner.pk)

            owner.gold += pack.price * (pack.percent / 100)
            owner.save()

            gold_log = GoldLog(player=owner, gold=pack.price * (pack.percent / 100), activity_txt='stckow')
            gold_log.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('chat', 'Новый стикерпак'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
