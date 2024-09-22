import datetime
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from math import floor

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.skill_training import SkillTraining
from player.player import Player
from player.views.get_subclasses import get_subclasses
from skill.models.excavation import Excavation
from skill.models.skill import Skill
from storage.models.stock import Stock, Good
from storage.models.storage import Storage
from wild_politics.settings import JResponse
from django.utils.translation import pgettext


# ускорить навык
@login_required(login_url='/')
@check_player
@transaction.atomic
def boost_skill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        skill_cls = None
        skill_obj = None
        cur_level = 0

        premium = False

        if player.premium > timezone.now():
            premium = True

        skill = request.POST.get('skill')

        skills_list = ['power', 'knowledge', 'endurance']

        pills_dict = {
            'power': Good.objects.get(name_ru='BCAA'),
            'knowledge': Good.objects.get(name_ru='Глицин'),
            'endurance': Good.objects.get(name_ru='Мельдоний'),
        }

        skill_classes = get_subclasses(Skill)

        for skill_cl in skill_classes:
            skills_list.append(skill_cl.__name__)

        if skill not in skills_list:
            data = {
                'response': pgettext('skills', 'Нет такого навыка'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        for skill_cl in skill_classes:
            if skill == skill_cl.__name__:
                skill_cls = skill_cl
                break

        if skill_cls:
            data = {
                'response': pgettext('skills', 'Нельзя ускорить навык'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                'response': pgettext('skills', 'Нет склада с бустерами в этом регионе'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        storage = Storage.actual.get(owner=player, region=player.region)

        # считаем, сколько бустеров надо
        boosters_need = getattr(player, skill) // 50 + 1

        if not Stock.objects.filter(storage=storage, stock__gte=boosters_need, good=pills_dict[skill]).exists():
            booster_name = pills_dict[skill].name
            data = {
                'response': pgettext('skills', "Недостаточно бустера %(booster_name)s. Требуется: %(boosters_need)s.") % {"booster_name": booster_name, "boosters_need": boosters_need},
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        skill_queue = SkillTraining.objects.filter(player=player).order_by('end_dtime')

        if not skill_queue:
            data = {
                'response': pgettext('skills', 'Очередь прокачки Характеристик пуста'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # Прокачивается тот навык, что хотят ускорить
        if not skill_queue[0].skill == skill:
            data = {
                'response': pgettext('skills', 'Вы прокачиваете другую Характеристику'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # проверяем что качаться еще более минуты
        if not (skill_queue[0].end_dtime > timezone.now()
                and skill_queue[0].end_dtime - timezone.now() > datetime.timedelta(seconds=300)):
            data = {
                'response': pgettext('skills', 'Нельзя ускорить последние пять минут улучшения'),
                'header': pgettext('skills', 'Ускорение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        skill_queue_u = []
        # смещение всех дат в секундах. Чтобы проще было пересчитать очередь
        shift = 0

        for index, item in enumerate(skill_queue):
            # сокращаем вдвое время для первой харатеристики
            if index == 0:
                # запишем изначальный срок прокачки, чтобы от него потом посчитать смещение
                current_endtime = item.end_dtime
                # берем дату, до которой качается навык
                # вычитаем из него текущее время, получаем инфу сколько секунд еще будет качаться
                # делим это на два и округляем вниз до целого числа (на всякий случай)
                # в виде секунд уменьшенное вдвое время прибавляем к текущему времени
                item.end_dtime = timezone.now() + datetime.timedelta(
                    seconds=floor((item.end_dtime - timezone.now()).total_seconds() / 2))
                # получаем смещение в секундах
                shift = (current_endtime - item.end_dtime).total_seconds()

            else:
                item.end_dtime = item.end_dtime - datetime.timedelta(seconds=shift)

            skill_queue_u.append(item)

        SkillTraining.objects.bulk_update(
            skill_queue_u,
            fields=['end_dtime', ],
            batch_size=len(skill_queue_u)
        )

        Stock.objects.filter(storage=storage, good=pills_dict[skill]).update(stock=F('stock') - boosters_need)

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('skills', 'Ускорение навыка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
