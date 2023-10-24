import json
import redis

from gov.models.custom_rights.custom_right import CustomRight
from gov.models.residency_request import ResidencyRequest
from player.player import Player
from region.models.region import Region


# кастомное право министра иностранных дел
class ForeignRights(CustomRight):

    # получить шаблон прав министра
    @staticmethod
    def get_form(state):

        requests = None
        history = []

        if state.residency == 'issue':
            requests = ResidencyRequest.objects.filter(state=state)

        else:
            r = redis.StrictRedis(host='redis', port=6379, db=0)

            counter = 0
            if r.zcard('res_ch_state_' + str(state.pk)) > 0:
                counter = r.zrevrange('res_ch_state_' + str(state.pk), 0, 0, withscores=True)[0][1]

            redis_list = r.zrevrangebyscore('res_ch_state_' + str(state.pk), counter + 1, 0, withscores=True)

            for scan in redis_list:
                dict = json.loads(scan[0])

                if not Player.objects.filter(pk=int(dict['char'])).exists():
                    r.zremrangebyscore('res_ch_state_' + str(state.pk), int(scan[1]), int(scan[1]))
                    continue

                if not Region.objects.filter(pk=int(dict['region'])).exists():
                    r.zremrangebyscore('res_ch_state_' + str(state.pk), int(scan[1]), int(scan[1]))
                    continue

                dict['char'] = Player.objects.get(pk=int(dict['char']))
                dict['region'] = Region.objects.get(pk=int(dict['region']))

                history.append(dict)

        data = {
            'requests': requests,
            'history': history,
        }
        return data, 'state/gov/forms/foreign_right.html'

    # получить шаблон прав министра
    @staticmethod
    def get_new_form(state):

        requests = None
        history = []

        if state.residency == 'issue':
            requests = ResidencyRequest.objects.filter(state=state)

        else:
            r = redis.StrictRedis(host='redis', port=6379, db=0)

            counter = 0
            if r.zcard('res_ch_state_' + str(state.pk)) > 0:
                counter = r.zrevrange('res_ch_state_' + str(state.pk), 0, 0, withscores=True)[0][1]

            redis_list = r.zrevrangebyscore('res_ch_state_' + str(state.pk), counter + 1, 0, withscores=True)

            for scan in redis_list:
                dict = json.loads(scan[0])

                if not Player.objects.filter(pk=int(dict['char'])).exists():
                    r.zremrangebyscore('res_ch_state_' + str(state.pk), int(scan[1]), int(scan[1]))
                    continue

                if not Region.objects.filter(pk=int(dict['region'])).exists():
                    r.zremrangebyscore('res_ch_state_' + str(state.pk), int(scan[1]), int(scan[1]))
                    continue

                dict['char'] = Player.objects.get(pk=int(dict['char']))
                dict['region'] = Region.objects.get(pk=int(dict['region']))

                history.append(dict)

        data = {
            'requests': requests,
            'history': history,
        }
        return data, 'state/redesign/forms/foreign_right.html'

    # Свойства класса
    class Meta:
        abstract = True
        verbose_name = "МИД"
        verbose_name_plural = "Министр иностранных дел"
