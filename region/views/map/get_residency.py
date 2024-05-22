# coding=utf-8
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
import redis
from player.decorators.player import check_player
from player.player import Player
from region.models.region import Region
from wild_politics.settings import JResponse
from gov.models.residency_request import ResidencyRequest
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.parliament_voting import ParliamentVoting
from gov.models.vote import Vote
from gov.models.presidential_voting import PresidentialVoting

# получить прописку
@login_required(login_url='/')
@check_player
@transaction.atomic
def get_residency(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
                'header': 'Получение прописки',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        try:
            # получаем айди региона
            region = int(json.loads(request.POST.get('region')))

        except ValueError:
            data = {
                'header': 'Получение прописки',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }
            return JsonResponse(data)

        if not Region.objects.filter(pk=region).exists():
            data = {
                'header': 'Получение прописки',
                'grey_btn': 'Закрыть',
                'response': 'Региона не существует',
            }
            return JsonResponse(data)

        region = Region.objects.get(pk=region)

        if not request.user.is_superuser \
                and region.limit_id and player.pk < region.limit_id:
            data = {
                'header': 'Получение прописки',
                'grey_btn': 'Закрыть',
                'response': 'Указанный регион закрыт для получения прописки',
            }
            return JResponse(data)

        if region.state:
            if region.state.residency == 'issue':
                if not ResidencyRequest.objects.filter(char=player, region=region, state=region.state).exists():

                    # если есть другие запросы - отменяем
                    ResidencyRequest.objects.filter(char=player).delete()

                    res_req = ResidencyRequest(
                        char=player,
                        region=region,
                        state=region.state
                    )
                    res_req.save()

                    data = {
                        'response': 'ok',
                    }
                    return JResponse(data)

                else:
                    data = {
                        'header': 'Запрос прописки',
                        'grey_btn': 'Закрыть',
                        'response': 'Заявка уже существует',
                    }
                    return JsonResponse(data)
            else:

                if Bulletin.objects.filter(
                                            voting__in=ParliamentVoting.objects.filter(running=True),
                                            player=player
                                                    ).exists():
                    Bulletin.objects.filter(
                        voting__in=ParliamentVoting.objects.filter(running=True),
                        player=player
                    ).delete()

                if Vote.objects.filter(
                        voting__in=PresidentialVoting.objects.filter(running=True),
                        player=player
                ).exists():
                    Vote.objects.filter(
                        voting__in=PresidentialVoting.objects.filter(running=True),
                        player=player
                    ).delete()

                player.residency = Region.objects.get(pk=region.pk)
                player.residency_date = timezone.now()
                player.save()

                r = redis.StrictRedis(host='redis', port=6379, db=0)

                counter = 0
                if r.zcard('res_ch_state_' + str(region.state.pk)) > 0:
                    counter = r.zrevrange('res_ch_state_' + str(region.state.pk), 0, 0, withscores=True)[0][1]

                dict = {
                    'char': str(player.pk),
                    'region': str(region.pk)
                }

                o_json = json.dumps(dict, indent=4)

                r.zadd('res_ch_state_' + str(region.state.pk), {o_json: int(counter) + 1})

                count = r.zcard('res_ch_state_' + str(region.state.pk))

                if count > 50:
                    r.zremrangebyrank('res_ch_state_' + str(region.state.pk), 0, 0)

                data = {
                    'response': 'ok',
                }
                return JResponse(data)
        else:
            player.residency = Region.objects.get(pk=region.pk)
            player.residency_date = timezone.now()
            player.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

    else:
        data = {
            'header': 'Получение прописки',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JResponse(data)
