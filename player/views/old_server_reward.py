from allauth.socialaccount.models import SocialAccount
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.utils import timezone

from ava_border.models.ava_border import AvaBorder
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from chat.models.sticker_pack import StickerPack
from chat.models.stickers_ownership import StickersOwnership


# начислить награды и вернуть их список
def old_server_rewards(player):
    cursor = connection.cursor()

    message = 'А мы тебя помним! На предыдущем сервере ты заработал:'

    changed = False

    if SocialAccount.objects.filter(user=player.account).exists():

        s_account = SocialAccount.objects.filter(user=player.account)
        uid = s_account[0].uid
        provider = s_account[0].provider

        sql_string = f"select * from public.rewards where uid = '{str(uid)}' and provider = '{provider}'"

        cursor.execute(sql_string)

        raw_rewards = cursor.fetchall()

        if raw_rewards:

            # премиум - аккаунт
            if raw_rewards[0][2] and raw_rewards[0][2] > player.premium:

                reward_dtime = raw_rewards[0][2]

                message += f' премиум-аккаунт до {reward_dtime.strftime("%Y-%m-%d")}'

                #  если есть активный премиум, то учитываем и его
                if player.premium > timezone.now():
                    delta = player.premium - timezone.now()
                    reward_dtime = reward_dtime + delta
                    message += f' (+{str(delta.days)}  дней за активный премиум);'

                player.premium = reward_dtime

                changed = True

            # премиум-карты
            if raw_rewards[0][3]:
                player.cards_count += int(raw_rewards[0][3])

                message += f' Wild Pass: {str(raw_rewards[0][3])};'

                changed = True

            # рамки
            if raw_rewards[0][4]:
                borders_count = 0
                # получаем list записей
                borders_list = raw_rewards[0][4].split(",")

                for border_id in borders_list:
                    if AvaBorder.objects.filter(pk=int(border_id)).exists():
                        border = AvaBorder.objects.get(pk=int(border_id))

                        if not AvaBorderOwnership.objects.filter(owner=player, border=border).exists():
                            ava_ship = AvaBorderOwnership(
                                owner=player,
                                border=border
                            )
                            ava_ship.save()
                            borders_count += 1

                            changed = True

                if borders_count > 0:
                    message += f' Рамок аватара: {str(borders_count)};'

            # рамки
            if raw_rewards[0][5]:
                stickers_count = 0
                add_gold = 0
                # получаем list записей
                stickers_list = raw_rewards[0][5].split(",")

                for stickers_id in stickers_list:
                    if StickerPack.objects.filter(pk=int(stickers_id)).exists():
                        pack = StickerPack.objects.get(pk=int(stickers_id))

                        if not StickersOwnership.objects.filter(owner=player, pack=pack).exists():
                            stick_ship = StickersOwnership(
                                owner=player,
                                pack=pack
                            )
                            stick_ship.save()
                            stickers_count += 1

                            changed = True

                        else:
                            player.gold += pack.price
                            add_gold += pack.price

                if stickers_count > 0 and add_gold > 0:
                    message += f' Наборы стикеров: {str(stickers_count)} (+{str(add_gold)} золота компенсации);'

                if stickers_count > 0 and add_gold == 0:
                    message += f' Наборы стикеров: {str(stickers_count)};'

            if changed:
                player.save()

            sql_string = f"delete from public.rewards where uid = '{str(uid)}' and provider = '{provider}'"

            cursor.execute(sql_string)

    if not changed:
        message = None

    return player, message
