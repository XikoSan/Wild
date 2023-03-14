import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.skill_training import SkillTraining
from player.player import Player
from wild_politics.settings import JResponse
from player.views.get_subclasses import get_subclasses
from skill.models.skill import Skill
from skill.models.excavation import Excavation

# изучить навык
@login_required(login_url='/')
@check_player
@transaction.atomic
def up_skill(request):
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

        skill_classes = get_subclasses(Skill)

        for skill_cl in skill_classes:
            skills_list.append(skill_cl.__name__)

        if skill not in skills_list:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Нет такого навыка',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
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
                    # 'response': _('positive_enrg_req'),
                    'response': 'Ваш уровень характеристик недостаточен',
                    'header': 'Изучение навыка',
                    'grey_btn': 'Закрыть',
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
                    # 'response': _('positive_enrg_req'),
                    'response': 'Данный навык изучен полностью или полностью запланирован',
                    'header': 'Изучение навыка',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

        if skill in ['power', 'knowledge', 'endurance']:
            if player.cash < ( (getattr(player, skill) + skill_cnt + 1) ** 2 ) * 10:
                data = {
                    # 'response': _('positive_enrg_req'),
                    'response': 'Недостаточно денег, необходимо: ' + str(((getattr(player, skill) + skill_cnt + 1) ** 2 ) * 10),
                    'header': 'Изучение навыка',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

        if not premium and SkillTraining.objects.filter(player=player).exists():
            data = {
                'response': 'Навык уже изучается',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if SkillTraining.objects.filter(player=player).count() > 5:
            data = {
                'response': 'Очередь навыков заполнена',
                'header': 'Изучение навыка',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if skill in ['power', 'knowledge', 'endurance']:
            player.cash -= ((getattr(player, skill) + skill_cnt + 1) ** 2 ) * 10

            CashLog.create(player=player, cash=0 - ((getattr(player, skill) + skill_cnt + 1) ** 2 ) * 10, activity_txt='skill')

        if skill in ['power', 'knowledge', 'endurance']:
            # время изучения навыка без према
            time_delta = datetime.timedelta(hours=(getattr(player, skill) + skill_cnt + 1))
            # с премом
            if player.premium > timezone.now():
                time_delta = datetime.timedelta(seconds=(getattr(player, skill) + skill_cnt + 1) * 2400)
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
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Изучение навыка',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
