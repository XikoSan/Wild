import re
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# изменить цвет партии в парламенте
@login_required(login_url='/')
@check_player
@transaction.atomic
def give_party_gold(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        if player.party_post:
            # если игрок действительно лидер партии
            if player.party_post.party_lead:

                changing_party = Party.objects.get(pk=player.party.pk)

                try:
                    gold_sum = int(request.POST.get('gold_sum'))

                except ValueError:
                    data = {
                        'response': pgettext('party_manage', 'Сумма золота - не число'),
                        'header': pgettext('party_manage', 'Выдача золота'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                if gold_sum < 1:
                    data = {
                        'response': pgettext('party_manage', 'Сумма золота должна быть не менее 1 ед.'),
                        'header': pgettext('party_manage', 'Выдача золота'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                if gold_sum > changing_party.gold:
                    data = {
                        'response': pgettext('party_manage', 'Сумма золота превышает баланс партии'),
                        'header': pgettext('party_manage', 'Выдача золота'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                try:
                    member_pk = int(request.POST.get('member'))

                except ValueError:
                    data = {
                        'response': pgettext('party_manage', 'ID персонажа должен быть целым числом'),
                        'header': pgettext('party_manage', 'Выдача золота'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                if not Player.objects.filter(pk=member_pk, party=changing_party).exists():
                    data = {
                        'response': pgettext('party_manage', 'Указанный игрок в партии не найден'),
                        'header': pgettext('party_manage', 'Выдача золота'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                player = Player.objects.get(pk=member_pk)
                player.gold += gold_sum
                player.save()

                changing_party.gold -= gold_sum
                changing_party.save()

                data = {
                    'response': 'ok',
                    'gold_val': changing_party.gold,

                    'payload': pgettext('party_manage', 'Выдано %(gold_sum)s золота') % {"gold_sum": gold_sum},
                    'header': pgettext('party_manage', 'Выдача золота'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

            else:
                data = {
                    'response': pgettext('party_manage', 'Вы не являетесь лидером партии'),
                    'header': pgettext('party_manage', 'Выдача золота'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('party_manage', 'Вы не состоите в партии'),
                'header': pgettext('party_manage', 'Выдача золота'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('party_manage', 'Выдача золота'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
