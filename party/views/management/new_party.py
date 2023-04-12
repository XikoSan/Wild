# from celery import uuid
# from celery.task.control import revoke

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from party.forms import NewPartyForm
from party.logs.membership_log import MembershipLog
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from player.logs.gold_log import GoldLog
from player.player import Player
from django.utils.translation import pgettext


# вкладка "Партия" главной страницы
@login_required(login_url='/')
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
                    # new_party.task_id = task_id.__str__()
                    new_party.save()
                    # Создаём должность лидера партии
                    leader_post = PartyPosition(title=pgettext('party_manage', 'Глава партии'), party=new_party, based=True, party_lead=True)
                    leader_post.save()
                    # Создаём должность новичка в партии
                    noob_post = PartyPosition(title=pgettext('party_manage', 'Новый игрок партии'), party=new_party, based=True)
                    noob_post.save()
                    # вызываем фоновый процесс старта праймериз на 7 дней
                    # GoPrims.apply_async((new_party.pk,), countdown=604800, queue='government', task_id=task_id)

                    # удаляем все его заявки в другие партии
                    PartyApply.objects.filter(player=player).delete()
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
            new_pty_frm = NewPartyForm()

            groups = list(player.account.groups.all().values_list('name', flat=True))
            page = 'party/new_party.html'
            if 'redesign' not in groups:
                page = 'party/redesign/new_party.html'
            # отправляем в форму
            return render(request, page,
                          {'player': player, 'new_party_form': new_pty_frm
                           })
