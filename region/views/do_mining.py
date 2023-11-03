# coding=utf-8
from decimal import Decimal
import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from state.models.state import State
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_stocks
from wild_politics.settings import JResponse
from skill.models.excavation import Excavation
from django.utils.translation import pgettext
import redis
from storage.models.stock import Stock, Good
from region.models.fossils import Fossils

# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def do_mining(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)
        gold_log = None

        if player.destination:
            data = {
                # 'response': pgettext('wait_flight_end'),
                'response': pgettext('mining', 'Дождитесь конца полёта'),
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            # return JResponse(data)
            return JResponse(data)
            # return HttpResponse('Дождитесь конца полёта')

        resource = request.POST.get('resource')

        if not Storage.actual.filter(owner=player, region=player.region).exists() \
                and resource != 'gold':
            data = {
                'response': pgettext('mining', 'У вас нет склада в этом регионе'),
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        # узнаем сколько он хочет потратить энергии
        count = request.POST.get('energy', '')

        if not count.isdigit():
            data = {
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('mining', 'Количество энергии - не число'),
            }
            return JResponse(data)

        count = int(count)

        # Количество Энергии должно быть положительным
        if count <= 0:
            data = {
                # 'response': pgettext('positive_enrg_req'),
                'response': pgettext('mining', 'Количество Энергии должно быть положительным'),
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)
        # Количество Энергии должно быть кратно десяти
        if count % 10 != 0:
            data = {
                # 'response': pgettext('mul_ten_enrg_req'),
                'response': pgettext('mining', 'Количество Энергии должно быть кратно десяти'),
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        if count > player.energy:
            data = {
                # 'response': pgettext('mul_ten_enrg_req'),
                'response': pgettext('mining', 'Недостаточно энергии'),
                'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JResponse(data)

        mined_result = {}
        mined_stocks_c = []
        mined_stocks_u = []

        if resource != 'gold':
            storage = Storage.actual.only('pk').get(owner=player, region=player.region)

        if resource == 'gold':
            # если запасов ресурса недостаточно
            if player.region.gold_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'response': pgettext('mul_ten_enrg_req'),
                    'response': pgettext('mining', 'Запасов золота в регионе недостаточно для добычи'),
                    'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                }
                return JResponse(data)

            player.gold += count / 10
            mined_result['gold'] = int(count / 10)

            # player.cash += count
            gold_log = GoldLog(player=player, gold=int(count / 10), activity_txt='mine')
            # mined_result['cash'] = count

            player.region.gold_has -= Decimal((count / 10) * 0.01)

        elif resource == 'oil':
            # если запасов ресурса недостаточно
            if int(player.region.oil_has * 100) < count / 10:
                data = {
                    # 'response': pgettext('mul_ten_enrg_req'),
                    'response': pgettext('mining', 'Запасов нефти в регионе недостаточно для добычи'),
                    'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                }
                return JResponse(data)
            # получаем запасы склада, с учетом блокировок
            goods = [player.region.oil_mark.name_ru]
            ret_stocks, ret_st_stocks = get_stocks(storage, goods)
            # облагаем налогом добытую нефть
            total_oil = (count / 10) * 20 * (1+ player.endurance * 0.01)

            if not player.account.date_joined + datetime.timedelta(days=7) > timezone.now():
                taxed_oil = State.get_taxes(player.region, total_oil, 'oil', player.region.oil_mark)
            else:
                taxed_oil = total_oil

            # сохраняем информацию о том, сколько добыто за день
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            # общее
            if r.exists("daily_" + player.region.oil_type):
                r.set("daily_" + player.region.oil_type, int(float(r.get("daily_" + player.region.oil_type))) + int(taxed_oil))
            else:
                r.set("daily_" + player.region.oil_type, int(taxed_oil))
            # регион
            if r.exists("daily_" + str(player.region.pk) + '_' + player.region.oil_type):
                r.set("daily_" + str(player.region.pk) + '_' +  player.region.oil_type, int(float(r.get("daily_" + str(player.region.pk) + '_' + player.region.oil_type))) + int(taxed_oil))
            else:
                r.set("daily_" + str(player.region.pk) + '_' +  player.region.oil_type, int(taxed_oil))

            # узнаем размерность товара и сколько в этой размерности занято
            sizetype_stocks = ret_st_stocks[player.region.oil_mark.size]
            # проверяем есть ли для него место на складе, с учетом блокировок
            if storage.capacity_check(player.region.oil_mark.size, taxed_oil, sizetype_stocks):
                # начислить нефть
                mined_result[player.region.oil_type] = taxed_oil

                stock, created = Stock.objects.get_or_create(storage=storage,
                                                             good=player.region.oil_mark
                                                             )
                stock.stock += taxed_oil
                mined_stocks_u.append(stock)

            else:
                # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                mined_result[player.region.oil_type] = getattr(storage, player.region.oil_mark.size + '_cap') - sizetype_stocks
                # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                stock, created = Stock.objects.get_or_create(storage=storage,
                                                             good=player.region.oil_mark
                                                             )
                stock.stock += ( getattr(storage, player.region.oil_mark.size + '_cap') - sizetype_stocks )

                mined_stocks_u.append(stock)

            player.region.oil_has -= Decimal((count / 10) * 0.01)

        elif resource == 'ore':
            # если запасов ресурса недостаточно
            if int(player.region.ore_has * 100) < count / 10:
                data = {
                    # 'response': pgettext('mul_ten_enrg_req'),
                    'response': pgettext('mining', 'Запасов руды в регионе недостаточно для добычи'),
                    'header': pgettext('mining', 'Ошибка добычи ресурсов'),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                }
                return JResponse(data)

            fossils_dict = {
                'Уголь': 'coal',
                'Железо': 'iron',
                'Бокситы': 'bauxite',
            }

            goods = []
            # запасы руд региона
            fossils = Fossils.objects.filter(region=player.region)

            for fossil in fossils:
                goods.append(fossil.good.name_ru)

            # lock_storage = get_storage(storage, goods)
            ret_stocks, ret_st_stocks = get_stocks(storage, goods)

            for mineral in fossils:
                # облагаем налогом добытую руду
                total_ore = (count / 50) * mineral.percent * (1+ player.endurance * 0.01)
                # экскавация
                if Excavation.objects.filter(player=player, level__gt=0).exists():
                    total_ore = Excavation.objects.get(player=player).apply({'sum': total_ore})

                if not player.account.date_joined + datetime.timedelta(days=7) > timezone.now():
                    taxed_ore = State.get_taxes(player.region, total_ore, 'ore', mineral.good)
                else:
                    taxed_ore = total_ore

                # сохраняем информацию о том, сколько добыто за день
                r = redis.StrictRedis(host='redis', port=6379, db=0)
                if r.exists("daily_" + fossils_dict[mineral.good.name_ru]):
                    r.set("daily_" + fossils_dict[mineral.good.name_ru],
                          int(float(r.get("daily_" + fossils_dict[mineral.good.name_ru]))) + int(taxed_ore))
                else:
                    r.set("daily_" + fossils_dict[mineral.good.name_ru], int(taxed_ore))
                # регион
                if r.exists("daily_" + str(player.region.pk) + '_' + fossils_dict[mineral.good.name_ru]):

                    r.set("daily_" + str(player.region.pk) + '_' + fossils_dict[mineral.good.name_ru],
                          int(float(r.get("daily_" + str(player.region.pk) + '_' + fossils_dict[mineral.good.name_ru]))) + int(taxed_ore))
                else:
                    r.set("daily_" + str(player.region.pk) + '_' + fossils_dict[mineral.good.name_ru], int(taxed_ore))

                # проверяем есть ли место на складе
                sizetype_stocks = ret_st_stocks[mineral.good.size]
                if storage.capacity_check(mineral.good.size, taxed_ore, sizetype_stocks):
                    # начислить минерал
                    mined_result[fossils_dict[mineral.good.name_ru]] = taxed_ore

                    stock, created = Stock.objects.get_or_create(storage=storage,
                                                                 good=mineral.good
                                                                 )
                    stock.stock += taxed_ore
                    mined_stocks_u.append(stock)

                    # актуализируем словарь по типоразмерам
                    if sizetype_stocks < getattr(storage, mineral.good.size + '_cap'):
                        ret_st_stocks[mineral.good.size] += taxed_ore
                    else:
                        ret_st_stocks[mineral.good.size] = getattr(storage, mineral.good.size + '_cap')

                else:
                    # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                    if taxed_ore > 0:
                        mined_result[fossils_dict[mineral.good.name_ru]] = getattr(storage, mineral.good.size + '_cap') - sizetype_stocks
                        # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                        stock, created = Stock.objects.get_or_create(storage=storage,
                                                                     good=mineral.good
                                                                     )
                        stock.stock += (getattr(storage, mineral.good.size + '_cap') - sizetype_stocks)

                        mined_stocks_u.append(stock)
                        # актуализируем словарь по типоразмерам
                        if sizetype_stocks < getattr(storage, mineral.good.size + '_cap'):
                            ret_st_stocks[mineral.good.size] += taxed_ore
                        else:
                            ret_st_stocks[mineral.good.size] = getattr(storage, mineral.good.size + '_cap')

            player.region.ore_has -= Decimal((count / 10) * 0.01)

        if mined_result:
            # обновляем существующие запасы
            if mined_stocks_u:
                Stock.objects.bulk_update(
                    mined_stocks_u,
                    fields=['stock',],
                    batch_size=len(mined_stocks_u)
                )

            if resource != 'gold':
                player.energy_cons(count)
            else:
                player.energy -= count
                player.save()

            if gold_log:
                gold_log.save()

            player.region.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': pgettext('mining', 'Ошибка добычи ресурсов'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JResponse(data)
