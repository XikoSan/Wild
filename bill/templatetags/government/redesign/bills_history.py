from itertools import chain

from django import template

register = template.Library()
from bill.models.bill import Bill
from player.views.get_subclasses import get_subclasses
from django.db import connection


@register.inclusion_tag('state/redesign/bills_history.html')
def bills_history(player, parliament):
    bills_list = []

    cursor = connection.cursor()

    sql_string = "with db_unions(pk, voting_end, cl) as ("
    bills_classes = get_subclasses(Bill)
    first = True
    for type in bills_classes:
        if not first:
            sql_string += " union "

        sql_string += "select id, voting_end, '" + str(type.__name__) + "' from " + type._meta.db_table + " where parliament_id = " + str(parliament.pk) + " and running = 'false'"

        if first:
            first = False

    sql_string += " ) select pk, cl from db_unions order by voting_end desc limit 50"

    cursor.execute(sql_string)
    raw_bills_hist = cursor.fetchall()

    # словарь: имя класса из сырого SQL - айди выбранных оттуда строк
    bills_dict = {}
    for item in raw_bills_hist:
        if item[1] in bills_dict.keys():
            bills_dict[item[1]].append(item[0])
        else:
            bills_dict[item[1]] = [item[0],]

    # словарь: имя класса из сырого SQL - объекты этого класса, которые были выбраны
    bill_instances_dict = {}
    for type in bills_classes:
        if type.__name__ in bills_dict:
            bill_instances_dict[type.__name__] = type.objects.filter(pk__in=bills_dict[type.__name__])

    # расставляем объекты по имеющейся хронологии
    for item in raw_bills_hist:
        if bills_list:
            # добавляем в список на вывод
            bills_list = list(chain(bills_list,
                                    bill_instances_dict[item[1]].filter(pk=item[0])
                                    ))
        else:
            bills_list = bill_instances_dict[item[1]].filter(pk=item[0])

    return {
        'player': player,
        'bills_list': bills_list,
    }
