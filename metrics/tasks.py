import datetime
import redis
from celery import shared_task
from datetime import timedelta
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from metrics.models.daily_cash import DailyCash
from metrics.models.daily_gold import DailyGold
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre
from party.party import Party
from region.models.region import Region
from storage.models.storage import Storage


@shared_task(name="save_daily")
def save_daily():
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    # ----------- золото -----------
    gold = 0
    if r.exists("daily_gold"):
        gold = int(r.get("daily_gold"))
        r.delete("daily_gold")

    DailyGold.objects.create(
        gold=gold
    )
    # очищаем информацию по регионам
    for region in Region.objects.all():
        if r.exists("daily_gold_" + str(region.pk)):
            r.delete("daily_gold_" + str(region.pk))

    # ----------- деньги -----------
    cash = 0
    if r.exists("daily_cash"):
        cash = int(r.get("daily_cash"))
        r.delete("daily_cash")

    DailyCash.objects.create(
        cash=cash
    )
    # очищаем информацию по регионам
    for region in Region.objects.all():
        if r.exists("daily_cash_" + str(region.pk)):
            r.delete("daily_cash_" + str(region.pk))

    # ----------- нефть -----------
    for oil_type in Region.oil_type_choices:
        oil = 0
        if r.exists("daily_" + oil_type[0]):
            oil = int(float(r.get("daily_" + oil_type[0])))
            r.delete("daily_" + oil_type[0])

        DailyOil.objects.create(
            oil=oil,
            type=oil_type[0]
        )

    # очищаем информацию по регионам
    for region in Region.objects.all():
        for oil_type in Region.oil_type_choices:
            if r.exists("daily_" + str(region.pk) + '_' + oil_type[0]):
                r.delete("daily_" + str(region.pk) + '_' + oil_type[0])

    # ----------- руды -----------
    for mineral in Storage.minerals.keys():
        ore = 0
        if r.exists("daily_" + mineral):
            ore = int(float(r.get("daily_" + mineral)))
            r.delete("daily_" + mineral)

        DailyOre.objects.create(
            ore=ore,
            type=mineral
        )

    # очищаем информацию по регионам
    for region in Region.objects.all():
        for mineral in Storage.minerals.keys():
            if r.exists("daily_" + str(region.pk) + '_' + mineral):
                r.delete("daily_" + str(region.pk) + '_' + mineral)

    # ----------- топ партий -----------
    # подбиваем недельные итоги
    if datetime.datetime.now().weekday() == 0:
        # берем сумму всех руд за прошедшую неделю
        date_now = datetime.datetime.now()
        date_7d = datetime.datetime.now() - timedelta(days=7)
        week_ore = DailyOre.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_ore=Sum('ore'))[
            'total_ore']
        # берем сумму всех марок нефти за прошедшую неделю
        week_oil = DailyOil.objects.filter(Q(date__gt=date_7d), Q(date__lt=date_now)).aggregate(total_oil=Sum('oil'))[
            'total_oil']

        r = redis.StrictRedis(host='redis', port=6379, db=0)

        parties = Party.objects.only('pk', 'image', 'title').filter(deleted=False)

        mining_dict = {}

        for party in parties:
            if r.exists("party_mining_" + str(party.pk)):
                mining_dict[party] = int(float(r.get("party_mining_" + str(party.pk))))
                r.set("party_mining_" + str(party.pk), 0)

        sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

        # идем по каждой партии
        for party_tuple in sorted_items:
            if party_tuple[1] > 0:
                # начисляем золото в процентном соотношении
                party_tuple[0].gold += int(15000 * (party_tuple[1] / (week_ore + week_oil)))
                party_tuple[0].save()

        all_skills = 0

        date_string = "2023-11-20"
        date = datetime.date.fromisoformat(date_string)

        if datetime.datetime.now().date() == date:
            for party in Party.objects.filter(deleted=False):
                # берем сколько она добыла за неделю
                if r.exists("party_skill_" + str(party.pk)):
                    all_skills += int(float(r.get("party_skill_" + str(party.pk))))
        else:
            if r.exists("all_skill"):
                all_skills = int(float(r.get("all_skill")))
                r.set("all_skill", 0)

        if all_skills > 0:
            mining_dict = {}

            for party in parties:
                if r.exists("party_skill_" + str(party.pk)):
                    mining_dict[party] = int(float(r.get("party_skill_" + str(party.pk))))
                    r.set("party_skill_" + str(party.pk), 0)

            sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

            # идем по каждой партии
            for party_tuple in sorted_items:
                # начисляем золото в процентном соотношении
                if party_tuple[1] > 0:
                    party_tuple[0].gold += 15000 * (party_tuple[1] / all_skills)
                    party_tuple[0].save()

        # производство
        all_produced = 0

        if datetime.datetime.now().date() == date:
            for party in Party.objects.filter(deleted=False):
                # берем сколько она добыла за неделю
                if r.exists("party_factory_" + str(party.pk)):
                    all_produced += int(float(r.get("party_factory_" + str(party.pk))))
        else:
            if r.exists("all_factory"):
                all_produced = int(float(r.get("all_factory")))
                r.set("all_factory", 0)

        if all_produced > 0:
            mining_dict = {}

            for party in parties:
                if r.exists("party_factory_" + str(party.pk)):
                    mining_dict[party] = int(float(r.get("party_factory_" + str(party.pk))))
                    r.set("party_factory_" + str(party.pk), 0)

            sorted_items = sorted(mining_dict.items(), key=lambda x: x[1], reverse=True)[:10]

            # идем по каждой партии
            for party_tuple in sorted_items:
                # начисляем золото в процентном соотношении
                if party_tuple[1] > 0:
                    party_tuple[0].gold += 15000 * (party_tuple[1] / all_produced)
                    party_tuple[0].save()
