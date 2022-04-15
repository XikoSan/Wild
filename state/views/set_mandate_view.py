from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
def set_mandate_view(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # если у игрока есть партия
    # и он в ней лидер
    if player.party\
            and player.party_post.party_lead:
        # если есть свободные мандаты
        if DeputyMandate.objects.filter(player=None).exists():
            # получаем депутатов: тех, у кого мандат уже есть
            deputates = DeputyMandate.objects.filter(party=player.party).exclude(player=None).values_list('player',
                                                                                                          flat=True)

            deputates_pk = []
            for deputate in deputates:
                deputates_pk.append(deputate)

            # получаем кандидатов: людей из партии, без мандата
            candidates = Player.objects.filter(party=player.party).exclude(pk__in=deputates_pk)

            # отправляем в форму
            return render(request, 'state/set_mandate.html', {
                # самого игрока
                'player': player,
                # список кандидатов
                'candidates': candidates,
            })

        else:
            return redirect('government')
    else:
        return redirect('government')
