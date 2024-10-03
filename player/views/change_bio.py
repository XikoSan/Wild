from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
from django.utils.translation import pgettext

# расход энергии со склада на пополнения её у персонажа
@login_required(login_url='/')
@check_player
@transaction.atomic
def change_bio(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

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
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('change_bio', 'Изменение описания профиля'),
            'grey_btn': pgettext('core', 'Закрыть')
        }
        return JResponse(data)
