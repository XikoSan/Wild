from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from storage.models.storage import Storage
from war.models.squads.infantry import Infantry
from war.models.wars.event_war import EventWar
from wild_politics.settings import JResponse


# запуск войны в текущем регионе
@login_required(login_url='/')
@check_player
@transaction.atomic
def send_squads(request):
    # todo:
    # проверять, что склад совпадает с регионом атаки или защиты
    # сделать универсальную отправку, а не только автоматы
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        rifle = 0

        try:
            rifle = int(request.POST.get('rifle'))

        except ValueError:
            data = {
                'response': 'Количество юнитов - не число',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if not Storage.objects.filter(owner=player, region=player.region).exists():
            data = {
                'response': 'Нет Склада отправки войск в регионе',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        storage = Storage.objects.get(owner=player, region=player.region)

        if getattr(storage, 'rifle') < rifle:
            data = {
                'response': 'Недостаточно войск',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # получаем войну
        war_pk = request.POST.get('war_id')

        if not EventWar.objects.filter(pk=int(war_pk), deleted=False, running=True).exists():
            data = {
                'response': 'Нет такой войны',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if not request.POST.get('side') in ['agr', 'def']:
            data = {
                'response': 'Нет такой стороны боя',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        war = EventWar.objects.get(pk=int(war_pk))

        if player.region != war.agr_region:
            data = {
                'response': 'Вы вне зоны боя',
                'header': 'Отправка войск',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        squad = None

        if Infantry.objects.filter(owner=player, object_id=int(war_pk), deleted=False, side=request.POST.get('side')).exists():
            squad = Infantry.objects.get(owner=player, object_id=int(war_pk), deleted=False, side=request.POST.get('side'))

        else:
            # создаем новый отряд
            squad = Infantry(
                owner=player,
                content_object=war,
                side=request.POST.get('side'),
                deploy=timezone.now()
            )

        setattr(squad, 'rifle', getattr(squad, 'rifle') + int(rifle))

        squad.save()

        setattr(storage, 'rifle', getattr(storage, 'rifle') - rifle)
        storage.save()

        data = {
            'response': 'ok',
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
