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
                        'response': 'Сумма золота - не число',
                        'header': 'Выдача золота',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                if gold_sum < 1:
                    data = {
                        'response': 'Сумма золота должна быть не менее 1 ед.',
                        'header': 'Выдача золота',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                if gold_sum > changing_party.gold:
                    data = {
                        'response': 'Сумма золота превышает баланс партии',
                        'header': 'Выдача золота',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                try:
                    member_pk = int(request.POST.get('member'))

                except ValueError:
                    data = {
                        'response': 'ID персонажа должен быть целым числом',
                        'header': 'Выдача золота',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                if not Player.objects.filter(pk=member_pk, party=changing_party).exists():
                    data = {
                        'response': 'Указанный игрок в партии не найден',
                        'header': 'Выдача золота',
                        'grey_btn': 'Закрыть',
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

                    'payload': f'Выдано {gold_sum} золота',
                    'header': 'Выдача золота',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            else:
                data = {
                    'response': pgettext('party_manage', 'Вы не являетесь лидером партии'),
                    'header': 'Выдача золота',
                    'grey_btn': _('Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('party_manage', 'Вы не состоите в партии'),
                'header': 'Выдача золота',
                'grey_btn': _('Закрыть'),
            }
            return JResponse(data)
    else:
        data = {
            'response': pgettext('mining', 'Ошибка метода'),
            'header': 'Выдача золота',
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
