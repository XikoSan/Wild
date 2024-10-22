import json
import redis
from django.utils.translation import pgettext_lazy

from gov.models.custom_rights.custom_right import CustomRight
from player.player import Player
from region.models.region import Region
from storage.models.storage import Storage


# просмотр добычи в регионах государства
class MiningStats(CustomRight):

    # получить шаблон прав министра
    @staticmethod
    def get_form(state):

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        region_dict = {}
        # получаем информацию по регионам
        for region in Region.objects.filter(state=state):
            region_dict[region] = {}

            # блестяшки
            if r.exists("daily_gold_" + str(region.pk)):
                region_dict[region]['gold'] = int(r.get("daily_gold_" + str(region.pk)))
            else:
                region_dict[region]['gold'] = 0

            # бабо$и
            if r.exists("daily_cash_" + str(region.pk)):
                region_dict[region]['cash'] = int(r.get("daily_cash_" + str(region.pk)))
            else:
                region_dict[region]['cash'] = 0

            for oil_type in Region.oil_type_choices:
                if oil_type[0] == region.oil_type:
                    if r.exists("daily_" + str(region.pk) + '_' + oil_type[0]):
                        region_dict[region][oil_type[0]] = int(r.get("daily_" + str(region.pk) + '_' + oil_type[0]))
                    else:
                        region_dict[region][oil_type[0]] = 0

            for mineral in Storage.minerals.keys():
                if r.exists("daily_" + str(region.pk) + '_' + mineral):
                    region_dict[region][mineral] = int(r.get("daily_" + str(region.pk) + '_' + mineral))
                else:
                    region_dict[region][mineral] = 0

        data = {
            'region_dict': region_dict,

            'minerals': Storage.minerals.keys(),
            'minerals_dict': Storage.minerals,

            'oils': Storage.oils.keys(),
            'oils_dict': Storage.oils,
        }
        return data, 'state/gov/forms/mining_stats.html'

    # получить шаблон прав министра
    @staticmethod
    def get_new_form(state):

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        region_dict = {}
        # получаем информацию по регионам
        for region in Region.objects.filter(state=state):
            region_dict[region] = {}

            # блестяшки
            if r.exists("daily_gold_" + str(region.pk)):
                region_dict[region]['gold'] = int(r.get("daily_gold_" + str(region.pk)))
            else:
                region_dict[region]['gold'] = 0

            # бабо$и
            if r.exists("daily_cash_" + str(region.pk)):
                region_dict[region]['cash'] = int(r.get("daily_cash_" + str(region.pk)))
            else:
                region_dict[region]['cash'] = 0

            for oil_type in Region.oil_type_choices:
                if oil_type[0] == region.oil_type:
                    if r.exists("daily_" + str(region.pk) + '_' + oil_type[0]):
                        region_dict[region][oil_type[0]] = int(r.get("daily_" + str(region.pk) + '_' + oil_type[0]))
                    else:
                        region_dict[region][oil_type[0]] = 0

            for mineral in Storage.minerals.keys():
                if r.exists("daily_" + str(region.pk) + '_' + mineral):
                    region_dict[region][mineral] = int(r.get("daily_" + str(region.pk) + '_' + mineral))
                else:
                    region_dict[region][mineral] = 0

        data = {
            'region_dict': region_dict,

            'minerals': Storage.minerals.keys(),
            'minerals_dict': Storage.minerals,

            'oils': Storage.oils.keys(),
            'oils_dict': Storage.oils,
        }
        return data, 'state/redesign/forms/mining_stats.html'

    # Свойства класса
    class Meta:
        abstract = True
        verbose_name = pgettext_lazy('minister_right', "Добыча сырья")
        verbose_name_plural = pgettext_lazy('minister_right', "Статистика добычи")
