from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate
from wild_politics.settings import JResponse


# изменение описания партии
@login_required(login_url='/')
@check_player
def switch_description(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии
        if not DeputyMandate.objects.filter(player=player, is_president=True).exists():
            data = {
                'response': pgettext('edit_state_descr', 'Вы не являетесь лидером государства'),
                'header': pgettext('edit_state_descr', 'Сообщение от государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        state = DeputyMandate.objects.get(player=player, is_president=True).parliament.state

        desk = request.POST.get('new_state_deskr')
        state.message = desk[:300]
        state.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
            'header': pgettext('edit_state_descr', 'Сообщение от государства'),
        }
        return JResponse(data)
