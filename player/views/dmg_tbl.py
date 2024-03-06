# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render
from datetime import datetime
import itertools


def calculate_damage(weapons, modifiers, energy_cost):
  """
  Рассчитывает итоговый урон оружия в зависимости от типа местности.

  Args:
    weapons: Словарь, где ключ - вид оружия, а значение - его базовый урон.
    modifiers: Таблица, где главный ключ - тип местности, а вторичный - вид оружия. Значение - множитель урона.

  Returns:
    Словарь, где ключ - тип местности через черту, а значение - словарь "вооружение - урон".
  """

  damage = {}
  for terrain_type1, terrain_type2 in itertools.product(modifiers.keys(), repeat=2):

    damage[f"{terrain_type1}-{terrain_type2}"] = {}

    for weapon, modifier1 in modifiers[terrain_type1].items():

      for weapon2, modifier2 in modifiers[terrain_type2].items():

        from player.logs.print_log import log
        if weapon == weapon2:
            if weapon == 'Танки':
                log(weapon)
                log(100 // energy_cost[weapon])
                log(weapons[weapon])
                log(modifier1)
                log(modifier2)

            modifier = 1
            if terrain_type1 == terrain_type2:
                modifier = modifier1
            else:
                modifier = modifier1 * modifier2

            damage[f"{terrain_type1}-{terrain_type2}"][weapon] = ( 100 // energy_cost[weapon] ) * weapons[weapon] * modifier

  return damage


def dmg_tbl(request):

    if not request.user.is_superuser:
        return redirect('overview')

    # Пример входных данных
    weapons = {
        "Танки": 100,
        "Мины": 22,
        "Автоматы": 6,
        "БМП": 41,
        "ПТ-орудия": 41,
        "БПЛА": 49,
        "Штурмовики": 164,
        "ПЗРК": 27,
    }

    energy_cost = {
        "Танки": 3,
        "Мины": 1,
        "Автоматы": 1,
        "БМП": 2,
        "ПТ-орудия": 2,
        "БПЛА": 2,
        "Штурмовики": 5,
        "ПЗРК": 1
    }

    terrain_table = {
        "равнины": {"Танки": 1, "Мины": 1, "Автоматы": 2, "БМП": 1.4, "ПТ-орудия": 0.6, "БПЛА": 0.9,
                    "Штурмовики": 1, "ПЗРК": 0.8},

        "леса": {"Танки": 0.8, "Мины": 1.5, "Автоматы": 1.4, "БМП": 1.5, "ПТ-орудия": 2, "БПЛА": 0.7,
                 "Штурмовики": 0.9, "ПЗРК": 1.5},

        "холмы": {"Танки": 1.0, "Мины": 1.5, "Автоматы": 1, "БМП": 1.2, "ПТ-орудия": 1.2, "БПЛА": 1.4,
                  "Штурмовики": 1.1, "ПЗРК": 0.8},

        "горы": {"Танки": 0.4, "Мины": 1, "Автоматы": 5.1, "БМП": 0.6, "ПТ-орудия": 1, "БПЛА": 1.0,
                 "Штурмовики": 0.4, "ПЗРК": 1.1},
    }

    # Вызов функции и вывод результата
    result = calculate_damage(weapons, terrain_table, energy_cost)


    return render(request, 'player/dmg_tbl.html', {
        'table': result,
    })
