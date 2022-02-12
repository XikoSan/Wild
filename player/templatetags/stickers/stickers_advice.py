from django import template

register = template.Library()
from state.models.treasury import Treasury
from storage.models.storage import Storage
from state.models.treasury_lock import TreasuryLock
from chat.models.sticker import Sticker
from chat.models.sticker_pack import StickerPack

# вх.: список записей владения стикерами
@register.inclusion_tag('player/stickers/advice.html')
def stickers_advice(stickers):

    stickers_header_dict = {}
    stickers_dict = {}

    if stickers:
        for sticker_own in stickers:
            # название пака
            stickers_header_dict[sticker_own.pack.pk] = sticker_own.pack.title
            # все его стикеры
            stickers_dict[sticker_own.pack.pk] = Sticker.objects.filter(pack=sticker_own.pack)

    return {
        # заголовки стикерпаков
        'stickers_header_dict': stickers_header_dict,
        # стикеры
        'stickers_dict': stickers_dict,
    }
