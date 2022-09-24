import datetime

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player
from war.models.squads.infantry import Infantry
from war.models.wars.war import War
from django.db.models import Sum
from django.db.models import F


# страница войн
@login_required(login_url='/')
@check_player
def open_war(request, class_name, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    try:
        war_class = apps.get_model('war', class_name)

    except KeyError:
        return redirect('war_page')

    if not war_class.objects.filter(pk=pk).exists():
        return redirect('war_page')

    war = war_class.objects.get(pk=pk)
    agr_side = war.war_side.get(side='agr', object_id=war.pk)
    def_side = war.war_side.get(side='def', object_id=war.pk)

    attrs_dict = war.get_attrs()

    # если у игрока есть отряды в этой войне
    squads_list = getattr(war, 'squads_list')
    squads_dict = {}

    agr_recon_dict = {}
    def_recon_dict = {}

    for squad_type in squads_list:
        if not hasattr(war, squad_type):
            continue

        # если у игрока есть отряды этого типа
        if getattr(war, squad_type).filter(owner=player, object_id=war.pk, deployed=False, deleted=False).exists():
            # получаем все отряды текущего типа этой войны
            squads_dict[squad_type] = getattr(war, squad_type).filter(owner=player, object_id=war.pk, deployed=False, deleted=False)

        # получаем сумму юнитов всех уже сформированных отрядов этого типа
        param = None
        # идем по всем юнитам этого типа отрядов
        for par in getattr(
                            apps.get_model('war', squad_type),
                            'specs').keys():
            if not param:
                param = F(par)
            else:
                param = param + F(par)

        args = [param,]

        if war.recon_balance < 1:
            # для атакующих
            agr_recon_dict[squad_type] = getattr(war, squad_type).filter(side='agr',
                                                                         object_id=war.pk,
                                                                         deleted=False).aggregate(
                                                                                                sum=Sum( *args )
                                                                                              )['sum']
        elif war.recon_balance > 1:
            # для обороны
            def_recon_dict[squad_type] = getattr(war, squad_type).filter(side='def',
                                                                         object_id=war.pk,
                                                                         deleted=False).aggregate(
                                                                                                sum=Sum( *args )
                                                                                              )['sum']


    # отправляем в форму
    return render(request, 'war/' + class_name + '.html', {
        # самого игрока
        'player': player,

        # война
        'war': war,
        # время окончания войны
        'end_time': war.start_time + datetime.timedelta(hours=24),

        # сторона атаки
        'agr_side': agr_side,
        # сторона обороны
        'def_side': def_side,

        # атрибуты класса
        'attrs_dict': attrs_dict,

        # мои отряды
        'squads_dict': squads_dict,

        # результаты разведки
        'agr_recon_dict': agr_recon_dict,
        'def_recon_dict': def_recon_dict,

        # класс войны
        'war_cl': War,
        # класс пехоты
        'infantry_cl': Infantry,
        # класс? бронетехники
        'light_cl': getattr(getattr(war, 'lightvehicle'), 'model'),

    })
