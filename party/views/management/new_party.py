# from celery import uuid
# from celery.task.control import revoke
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from party.forms import NewPartyForm
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player
from django_celery_beat.models import IntervalSchedule, PeriodicTask


# from gamecore.tasks import GoPrims


# вкладка "Партия" главной страницы
@login_required(login_url='/')
def new_party(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
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
                    # new_party.task_id = task_id.__str__()
                    new_party.save()

                    if player.pk == 1:
                        periods_types = [IntervalSchedule.DAYS,
                                         IntervalSchedule.HOURS,
                                         IntervalSchedule.MINUTES]

                        periods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

                        count = 0

                        for p_type in periods_types:

                            for period in periods:
                                schedule, created = IntervalSchedule.objects.get_or_create(every=period,
                                                                                           period=p_type)
                                task = PeriodicTask.objects.create(
                                    name=str(count),
                                    task='delayed_task',
                                    interval=schedule,
                                    args=json.dumps([count]),
                                    start_time=timezone.now()
                                )

                                count += 1

                    # Создаём должность лидера партии
                    leader_post = PartyPosition(title='Глава партии', party=new_party, based=True, party_lead=True)
                    leader_post.save()
                    # Создаём должность новичка в партии
                    noob_post = PartyPosition(title='Новый игрок партии', party=new_party, based=True)
                    noob_post.save()
                    # вызываем фоновый процесс старта праймериз на 7 дней
                    # GoPrims.apply_async((new_party.pk,), countdown=604800, queue='government', task_id=task_id)

                    # удаляем все его заявки в другие партии
                    PartyApply.objects.filter(player=player).delete()
                    # назначаем игроку его партию
                    player.party = new_party
                    # Даем игроку пост в новой партии
                    player.party_post = leader_post
                    player.save()
                    return redirect('party')
                else:
                    return redirect('party')
            else:
                return redirect('party')
        # если страницу только грузят
        else:
            new_pty_frm = NewPartyForm()
            # отправляем в форму
            return render(request, 'party/new_party.html',
                          {'player': player, 'new_party_form': new_pty_frm
                           })
