from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate
from wild_politics.settings import JResponse
from django.utils.translation import pgettext


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_mandate(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если у игрока есть партия
        # и он в ней лидер
        if player.party \
                and player.party_post.party_lead:
            # если есть свободные мандаты
            if DeputyMandate.objects.filter(player=None, party=player.party).exists():
                candidate_pk = request.POST.get('candidate')
                # проверяем, есть ли такой игрок в этой партии
                if not Player.objects.filter(pk=int(candidate_pk), party=player.party).exists():
                    data = {
                        'response': pgettext('set_mandate', 'В партии нет такого кандидата'),
                        'header': pgettext('set_mandate', 'Выдача мандата'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                candidate = Player.get_instance(pk=int(candidate_pk))

                # проверяем, есть ли мандат с таким кадитатом:
                if DeputyMandate.objects.filter(player=candidate).exists():
                    data = {
                        'response': pgettext('set_mandate', 'У кандидата уже есть мандат'),
                        'header': pgettext('set_mandate', 'Выдача мандата'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)

                # получаем первый свободный мандат
                mandate = DeputyMandate.objects.select_for_update().filter(player=None, party=player.party).first()

                mandate.player = candidate
                mandate.save()

                data = {
                    'response': pgettext('set_mandate', 'Мандат успешно выдан'),
                    'header': pgettext('set_mandate', 'Выдача мандата'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

            else:
                data = {
                    'response': pgettext('set_mandate', 'Нет свободных мандатов'),
                    'header': pgettext('set_mandate', 'Выдача мандата'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)
        else:
            data = {
                'response': pgettext('set_mandate', 'Вы - не лидер партии'),
                'header': pgettext('set_mandate', 'Выдача мандата'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('set_mandate', 'Выдача мандата'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
