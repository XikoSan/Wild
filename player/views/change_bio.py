from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# расход энергии со склада на пополнения её у персонажа
@login_required(login_url='/')
@check_player
@transaction.atomic
def change_bio(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        bio = request.POST.get('bio')

        player.bio = bio[:250]
        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Пополнение энергии',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
