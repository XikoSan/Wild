# from celery import uuid
# from celery.task.control import revoke

import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import pgettext
from datetime import datetime, timedelta
import random

from party.forms import NewPartyForm
from party.logs.membership_log import MembershipLog
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from django.db.models import F, Sum

# вкладка "Партия" главной страницы
@login_required(login_url='/')
@check_player
def new_party(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # если игрок состоит в партии
    if player.party:
        return redirect('party')
    # если у него нет партии
    else:
        # если из формы вернули заявку на новую партию
        if request.method == "POST":
            if player.gold >= 10:
                # форма для новой партии
                new_pty_frm = NewPartyForm(request.POST, request.FILES)
                # если форма заполненна корректно
                player.gold = player.gold - 10
                if new_pty_frm.is_valid():
                    new_party = new_pty_frm.save(commit=False)
                    # task_id = uuid()
                    # Новые партии создаются по месту нахождения игрока
                    new_party.region = player.region
                    # сохраняем дату основания
                    new_party.foundation_date = timezone.now()
                    # день праймериз
                    new_party.primaries_day = new_party.foundation_date.weekday()
                    # new_party.task_id = task_id.__str__()
                    new_party.save()
                    # Создаём должность лидера партии
                    leader_post = PartyPosition(title=pgettext('party_manage', 'Глава партии'), party=new_party,
                                                based=True, party_lead=True)
                    leader_post.save()
                    # Создаём должность новичка в партии
                    noob_post = PartyPosition(title=pgettext('party_manage', 'Новый игрок партии'), party=new_party,
                                              based=True)
                    noob_post.save()
                    # вызываем фоновый процесс старта праймериз на 7 дней
                    # GoPrims.apply_async((new_party.pk,), countdown=604800, queue='government', task_id=task_id)

                    # удаляем все его заявки в другие партии
                    PartyApply.objects.filter(player=player, status='op').update(status='cs')
                    # назначаем игроку его партию
                    player.party = new_party
                    # Даем игроку пост в новой партии
                    player.party_post = leader_post

                    gold_log = GoldLog(player=player, gold=-10, activity_txt='party')
                    gold_log.save()

                    player.save()
                    # Логировние: создаем запись о вступлении
                    party_log = MembershipLog(player=player, dtime=timezone.now(),
                                              party=new_party)
                    party_log.save()
                    return redirect('party')
                else:
                    return redirect('party')
            else:
                return redirect('party')
        # если страницу только грузят
        else:
            skill_sum = 10
            new_pty_frm = None
            sorted_chars = None
            party_sizes = {}

            if player.power + player.knowledge + player.endurance < 10:
                skill_sum = player.power + player.knowledge + player.endurance

                # -----------------

                # Получаем всех игроков, которые являются главами партий
                party_leads = Player.objects.annotate(
                    total_stats=F('power') + F('knowledge') + F('endurance')
                ).filter(
                    party_post__party_lead=True,
                    total_stats__gte=10
                )

                # Создаем подключение к Redis
                r = redis.StrictRedis(host='redis', port=6379, db=0)

                # Создаем список кортежей (игрок, время последнего онлайна), фильтруем по времени
                chars_with_online_time = []

                for char in party_leads:
                    # Получаем timestamp последнего онлайна игрока из Redis
                    last_online_timestamp = r.hget('online', str(char.pk))

                    if last_online_timestamp:
                        # Преобразуем в целое число, если timestamp найден
                        last_online_timestamp = int(last_online_timestamp)

                        # Проверяем разницу во времени
                        last_online_time = datetime.fromtimestamp(last_online_timestamp)
                        if datetime.now() - last_online_time <= timedelta(days=1):
                            chars_with_online_time.append((char, last_online_time))

                # Сортируем список по времени последнего онлайна (от самого свежего)
                chars_with_online_time.sort(key=lambda x: x[1], reverse=True)

                # Получаем отсортированный список игроков
                sorted_chars = [char for char, _ in chars_with_online_time]

                # Перемешиваем первые 10 записей
                first_ten = sorted_chars[:10]
                random.shuffle(first_ten)

                # Объединяем перемешанные первые 10 записей с остальными
                result = first_ten + sorted_chars[10:]
                sorted_chars = result

                # -----------------

                for sorted_char in sorted_chars:
                    party_sizes[sorted_char.party] = Player.objects.filter(party=sorted_char.party).count()

            else:
                new_pty_frm = NewPartyForm()

            page = 'party/redesign/new_party.html'
            # отправляем в форму
            return render(request, page,
                          {'player': player,
                           'page_name': pgettext('new_party', 'Новая партия'),
                           'new_party_form': new_pty_frm,

                           'skill_sum': skill_sum,
                           'sorted_chars': sorted_chars,
                           'sizes': party_sizes
                           })
