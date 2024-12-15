import datetime
import redis
from celery import shared_task
from datetime import timedelta
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from gov.models.minister import Minister
from metrics.models.daily_cash import DailyCash
from metrics.models.daily_gold import DailyGold
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre
from party.party import Party
from region.models.region import Region
from storage.models.storage import Storage
from player.logs.gold_log import GoldLog
from metrics.models.daily_gold_by_state import DailyGoldByState
from datetime import timedelta
from django.db.models import Sum, F, FloatField, Case, When
from django.utils.timezone import now
from gov.models.president import President
from state.models.parliament.parliament_party import ParliamentParty
from math import ceil
from party.logs.party_gold_log import PartyGoldLog


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

    daily_gold_by_state = {}
    daily_fin_gold_by_state = {}

    # Очищаем информацию по регионам
    for region in Region.objects.all():
        cache_key = "daily_gold_" + str(region.pk)
        gold = 0
        if r.exists(cache_key):
            gold = int(r.get(cache_key))

            # Если у региона есть связанное state, накапливаем gold
            if region.state:
                state_id = region.state.pk
                if state_id in daily_gold_by_state:
                    daily_gold_by_state[state_id] += gold
                else:
                    daily_gold_by_state[state_id] = gold

            # Удаляем запись из кеша
            r.delete(cache_key)

        # информация о добытом после выкапывания дейлика
        cache_key = "daily_fin_gold_" + str(region.pk)
        gold = 0
        if r.exists(cache_key):
            gold = int(r.get(cache_key))

            # Если у региона есть связанное state, накапливаем gold
            if region.state:
                state_id = region.state.pk
                if state_id in daily_fin_gold_by_state:
                    daily_fin_gold_by_state[state_id] += gold
                else:
                    daily_fin_gold_by_state[state_id] = gold

            # Удаляем запись из кеша
            r.delete(cache_key)

    # Создаём объекты DailyGoldByState с накопленными значениями
    daily_u = [
        DailyGoldByState(
            state_id=state_id,
            gold=gold,
            daily_gold=daily_fin_gold_by_state.get(state_id, 0),
            # Заполняем daily_gold из daily_fin_gold_by_state или 0
            date=timezone.now()
        )
        for state_id, gold in daily_gold_by_state.items()
    ]

    if len(daily_u) > 0:
        DailyGoldByState.objects.bulk_create(
            daily_u,
            batch_size=len(daily_u)
        )
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

        # ------------------------------------------------------------------------------------------

        # 1. Определяем дату 7 дней назад
        seven_days_ago = now().date() - timedelta(days=7)

        # 2. Суммируем заработанное всеми государствами за последние 7 дней
        total_gold_last_7_days = DailyGoldByState.objects.filter(
            date__gte=seven_days_ago
        ).aggregate(total_gold=Sum('daily_gold'))['total_gold'] or 0

        # 3. Получаем данные по каждому государству: сколько они заработали и какой это процент
        states_with_percentages = DailyGoldByState.objects.filter(
            date__gte=seven_days_ago
        ).values('state__pk').annotate(
            state_total=Sum('daily_gold'),
            percentage=Case(
                When(state_total=0, then=0.0),  # Если заработок нулевой
                default=F('state_total') / total_gold_last_7_days,  # Иначе вычисляем процент
                output_field=FloatField(),
            )
        )

        # 4. Распределяем золото лидерам президентских государств
        for state_data in states_with_percentages:
            state_pk = state_data['state__pk']
            percentage = state_data['percentage'] or 0.0

            # Вычисляем бонус
            gold_bonus = ceil(10000 * percentage * 0.33)

            # Находим президента
            try:
                president = President.objects.get(state__pk=state_pk)
                leader = president.leader

                if leader:
                    # Добавляем золото лидеру
                    leader.gold = F('gold') + gold_bonus
                    leader.save(update_fields=['gold'])

                    GoldLog(player=leader, gold=gold_bonus, activity_txt='leadzp').save()

                else:
                    continue

            except President.DoesNotExist:
                continue

            # если есть министры
            if Minister.objects.filter(state__pk=state_pk).exists():
                # их треть золота делим на число министров
                minister_bonus = ceil(gold_bonus / Minister.objects.filter(state__pk=state_pk).count())

                # для каждого министра
                for minister in Minister.objects.filter(state__pk=state_pk):
                    # если есть
                    if minister.player:
                        # Добавляем золото министру
                        minister.player.gold = F('gold') + minister_bonus
                        minister.player.save(update_fields=['gold'])

                        GoldLog(player=minister.player, gold=minister_bonus, activity_txt='min_zp').save()

            if ParliamentParty.objects.filter(parliament__state__id=state_pk).exists():
                # для каждой парламентской партии
                for pparty in ParliamentParty.objects.filter(parliament__state__id=state_pk):
                    # каждая партия получает пропорционально числу мест в парламенте
                    pparty_bonus = ceil(gold_bonus * (pparty.seats / 100))

                    # Добавляем золото партии
                    pparty.party.gold = F('gold') + pparty_bonus
                    pparty.party.save(update_fields=['gold'])

                    PartyGoldLog(party=pparty.party, gold=pparty_bonus, activity_txt='parl_zp').save()

        # ------------------------------------------------------------------------------------------

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
                party_tuple[0].gold += int(10000 * (party_tuple[1] / (week_ore + week_oil)))
                party_tuple[0].save()

                PartyGoldLog(party=party_tuple[0], gold=int(10000 * (party_tuple[1] / (week_ore + week_oil))), activity_txt='rating').save()

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
                    party_tuple[0].gold += 10000 * (party_tuple[1] / all_skills)
                    party_tuple[0].save()

                    PartyGoldLog(party=party_tuple[0], gold=int(10000 * (party_tuple[1] / all_skills)),
                                 activity_txt='rating').save()

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
                    party_tuple[0].gold += 10000 * (party_tuple[1] / all_produced)
                    party_tuple[0].save()

                    PartyGoldLog(party=party_tuple[0], gold=int(10000 * (party_tuple[1] / all_produced)),
                                 activity_txt='rating').save()
