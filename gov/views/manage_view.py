from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate


# управление государством (президентом)
@login_required(login_url='/')
@check_player
def manage_view(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if not DeputyMandate.objects.filter(player=player, is_president=True).exists():
        return redirect('government')

    # гос
    state = DeputyMandate.objects.get(player=player, is_president=True).parliament.state

    # отправляем в форму
    return render(request, 'state/redesign/gov/manage.html', {
        'page_name': pgettext('set_mandate', 'Управление государством'),
        # самого игрока
        'player': player,
        # государство
        'state': state,
    })