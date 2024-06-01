from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from wild_politics.settings import JResponse


@login_required(login_url='/')
@check_player
# выбор рамки
def choose_border(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        try:
            border_id = int(request.POST.get('border_id'))

        except ValueError:
            return {
                'header': 'Выбор рамки',
                'grey_btn': 'Закрыть',
                'response': 'ID рамки должен быть целым числом',
            }

        # сбросить самолет до дефолтного
        if border_id == 0:
            AvaBorderOwnership.objects.filter(owner=player).update(in_use=False)

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        #  выбор другого самолёта
        if AvaBorderOwnership.objects.filter(owner=player, pk=border_id).exists():
            border = AvaBorderOwnership.objects.get(pk=border_id)
            border.in_use = True
            border.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            return {
                'header': 'Выбор рамки',
                'grey_btn': 'Закрыть',
                'response': 'Указанная рамка вам не принадлежит',
            }

    # если страницу только грузят
    else:
        data = {
            'response': _('Ошибка метода'),
            'header': 'Выбор рамки',
            'grey_btn': _('Закрыть'),
        }
        return JResponse(data)
