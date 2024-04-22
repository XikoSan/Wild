# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render
from datetime import datetime
import itertools


def skill_tbl(request):
    """
    Показывает темпы прокачки игрока (на примере одной характеристики).

    """

    if not request.user.is_superuser:
        return redirect('overview')

    # таблица уровень - количество дней до момента, как можно будет что-то прокачать
    result = [
        [0, 1, 1, 1],
    ]

    skill_levels = {
        'pwr': 1,
        'int': 1,
        'end': 1,
    }

    earning = 15300
    price = 40
    balance = 10000

    # дней с прокачки последнего навыка
    day = 0

    # первый день игры
    while balance >= price:

        cheapest = None
        ch_price = None
        # выбираем самый дешевый навык
        for i_skill in skill_levels.keys():
            if not ch_price or ch_price > ((skill_levels[i_skill] + 1) ** 2) * 10 :
                cheapest = i_skill
                ch_price = ((skill_levels[i_skill] + 1) ** 2) * 10

        balance -= ch_price

        skill_levels[cheapest] += 1
        result.append([day, skill_levels['pwr'], skill_levels['int'], skill_levels['end']])
        day = 0

        earning = 15000 + ((skill_levels['pwr'] + skill_levels['int'] + skill_levels['end']) * 100)

    limit = 200

    while skill_levels['pwr'] < limit and skill_levels['int'] < limit and skill_levels['end'] < limit:
        day += 1
        balance += earning

        while balance >= price:

            cheapest = None
            ch_price = None
            # выбираем самый дешевый навык
            for i_skill in skill_levels.keys():
                if not ch_price or ch_price > ((skill_levels[i_skill] + 1) ** 2) * 10:
                    cheapest = i_skill
                    ch_price = ((skill_levels[i_skill] + 1) ** 2) * 10

            balance -= ch_price

            skill_levels[cheapest] += 1
            result.append([day, skill_levels['pwr'], skill_levels['int'], skill_levels['end']])
            day = 0

            pwr_earn = 0
            # if skill_levels['pwr'] > 100:
            if False:
                pwr_earn = ( (skill_levels['pwr'] - 100) * 200 ) + 10000
            else:
                pwr_earn = skill_levels['pwr'] * 100

            int_earn = 0
            # if skill_levels['int'] > 100:
            if False:
                int_earn = ( (skill_levels['int'] - 100) * 200 ) + 10000
            else:
                int_earn = skill_levels['int'] * 100

            end_earn = 0
            # if skill_levels['end'] > 100:
            if False:
                end_earn = ( (skill_levels['end'] - 100) * 200 ) + 10000
            else:
                end_earn = skill_levels['end'] * 100

            earning = 15000 + pwr_earn + int_earn + end_earn

    return render(request, 'player/skill_tbl.html', {
        'table': result,
    })
