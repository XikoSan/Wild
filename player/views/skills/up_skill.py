import datetime
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.skill_training import SkillTraining
from player.player import Player
from player.views.get_subclasses import get_subclasses
from skill.models.excavation import Excavation
from skill.models.skill import Skill
from wild_politics.settings import JResponse
from django.utils.translation import pgettext
from player.views.multiple_sum import multiple_sum


# изучить навык
@login_required(login_url='/')
@check_player
@transaction.atomic
def up_skill(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # fingerprinting
        if request.POST.get('fprint'):
            player.fingerprint = request.POST.get('fprint')
        else:
            data = {
                'response': pgettext('skills', 'Отсутствует обязательный аргумент запроса'),
                'header': pgettext('skills', 'Изучение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        skill_cls = None
        skill_obj = None
        cur_level = 0

        premium = False

        if player.premium > timezone.now():
            premium = True

        skill = request.POST.get('skill')

        skills_list = ['power', 'knowledge', 'endurance']

        skill_classes = get_subclasses(Skill)

        for skill_cl in skill_classes:
            skills_list.append(skill_cl.__name__)

        if skill not in skills_list:
            data = {
                'response': pgettext('skills', 'Нет такого навыка'),
                'header': pgettext('skills', 'Изучение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        for skill_cl in skill_classes:
            if skill == skill_cl.__name__:
                skill_cls = skill_cl
                break

        if skill_cls:
            has_right = skill_cls.check_has_right(player)

            if not has_right:
                data = {
                    'response': pgettext('skills', 'Ваш уровень характеристик недостаточен'),
                    'header': pgettext('skills', 'Изучение навыка'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        # считаем, сколько у нас изучается навыков с этим именем
        skill_cnt = SkillTraining.objects.filter(player=player, skill=skill).count()

        if skill_cls:
            if skill_cls.objects.filter(player=player).exists():
                skill_obj = skill_cls.objects.get(player=player)

                if skill_obj:
                    cur_level = getattr(skill_obj, 'level')
                else:
                    cur_level = 0

            if cur_level + skill_cnt >= skill_cls.max_level:
                data = {
                    'response': pgettext('skills', 'Данный навык изучен полностью или полностью запланирован'),
                    'header': pgettext('skills', 'Изучение навыка'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        if skill in ['power', 'knowledge', 'endurance']:
            if player.cash < multiple_sum(((getattr(player, skill) + skill_cnt + 1) ** 2) * 10):
                data = {
                    'response': pgettext('skills', 'Недостаточно денег, необходимо: ') + str(
                        ((getattr(player, skill) + skill_cnt + 1) ** 2) * 10),
                    'header': pgettext('skills', 'Изучение навыка'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        if not premium and SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': pgettext('skills', 'Навык уже изучается'),
                'header': pgettext('skills', 'Изучение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if SkillTraining.objects.filter(player=player).count() > 5:
            data = {
                'response': pgettext('skills', 'Очередь навыков заполнена'),
                'header': pgettext('skills', 'Изучение навыка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if skill in ['power', 'knowledge', 'endurance']:
            player.cash -= multiple_sum(((getattr(player, skill) + skill_cnt + 1) ** 2) * 10)

            CashLog.create(player=player, cash=0 - multiple_sum(((getattr(player, skill) + skill_cnt + 1) ** 2) * 10),
                           activity_txt='skill')

        if skill in ['power', 'knowledge', 'endurance']:
            # ивентовый буст к прокачке
            ActivityEvent = apps.get_model('event.ActivityEvent')
            ActivityEventPart = apps.get_model('event.ActivityEventPart')
            ActivityGlobalPart = apps.get_model('event.ActivityGlobalPart')

            boost = 1

            if ActivityEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                            event_end__gt=timezone.now()).exists():

                event = ActivityEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                                     event_end__gt=timezone.now()).first()

                if ActivityEventPart.objects.filter(player=player, event=event).exists():
                    boost = 1 - ActivityEventPart.objects.get(player=player, event=event).boost / 100

            # время изучения навыка без према
            time_delta = datetime.timedelta(seconds=int((getattr(player, skill) + skill_cnt + 1) * 3600 * boost))
            # с премом
            if player.premium > timezone.now():
                time_delta = datetime.timedelta(seconds=int((getattr(player, skill) + skill_cnt + 1) * 2400 * boost))
        else:
            if skill_obj:
                cur_level = getattr(skill_obj, 'level')

            else:
                cur_level = 0

            # время изучения навыка без према
            time_delta = datetime.timedelta(hours=(cur_level + skill_cnt + 1))
            # с премом
            if player.premium > timezone.now():
                time_delta = datetime.timedelta(seconds=(cur_level + skill_cnt + 1) * 2400)

        start = timezone.now()
        if SkillTraining.objects.filter(player=player).exists():
            # если есть навыки в очереди, берем время завершения от последнего
            start = SkillTraining.objects.filter(player=player).order_by('end_dtime').last().end_dtime

        new_skill = SkillTraining(
            player=player,
            skill=skill,
            end_dtime=start + time_delta,
        )

        new_skill.save()
        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('skills', 'Изучение навыка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
