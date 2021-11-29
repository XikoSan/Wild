from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate
from wild_politics.settings import JResponse


# проголосовать на выборах в парламент государства
@login_required(login_url='/')
@check_player
@transaction.atomic
def set_mandate(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

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
                        'response': 'В партии нет такого кандидата',
                        'header': 'Выдача мандата',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                candidate = Player.objects.get(pk=int(candidate_pk))

                # проверяем, есть ли мандат с таким кадитатом:
                if DeputyMandate.objects.filter(player=candidate).exists():
                    data = {
                        'response': 'У кандидата уже есть мандат',
                        'header': 'Выдача мандата',
                        'grey_btn': 'Закрыть',
                    }
                    return JResponse(data)

                # получаем первый свободный мандат
                mandate = DeputyMandate.objects.select_for_update().filter(player=None, party=player.party).first()

                mandate.player = candidate
                mandate.save()

                data = {
                    'response': 'Мандат успешно выдан',
                    'header': 'Выдача мандата',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            else:
                data = {
                    'response': 'Нет свободных мандатов',
                    'header': 'Выдача мандата',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)
        else:
            data = {
                'response': 'Вы - не лидер партии',
                'header': 'Выдача мандата',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Основание государства',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
