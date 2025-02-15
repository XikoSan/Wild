# Generated by Django 3.1.3 on 2023-07-15 13:35

from django.db import migrations
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

class Migration(migrations.Migration):

    def move_volumes(apps, schema_editor):
        Good = apps.get_model('storage', 'Good')

        # ------vvvvvvv------Все типы товаров------vvvvvvv------
        types = {
            'minerals': pgettext_lazy('goods', 'Минералы'),
            'oils': pgettext_lazy('goods', 'Нефть'),
            'materials': pgettext_lazy('goods', 'Материалы'),
            'equipments': pgettext_lazy('goods', 'Оборудование'),
            'units': pgettext_lazy('goods', 'Оружие'),
        }
        # ------vvvvvvv------Минералы на складе------vvvvvvv------
        minerals = {
            # Уголь
            'coal': pgettext_lazy('goods', 'Уголь'),
            # Железо
            'iron': pgettext_lazy('goods', 'Железо'),
            # Бокситы
            'bauxite': pgettext_lazy('goods', 'Бокситы'),
        }
        # ------vvvvvvv------Нефть на складе------vvvvvvv------
        oils = {
            'wti_oil': pgettext_lazy('goods', 'Нефть WTI'),

            'brent_oil': pgettext_lazy('goods', 'Нефть Brent'),

            'urals_oil': pgettext_lazy('goods', 'Нефть Urals'),
        }
        # ------vvvvvvv------Материалы на складе------vvvvvvv------
        materials = {
            'gas': pgettext_lazy('goods', 'Бензин'),

            'diesel': pgettext_lazy('goods', 'Дизельное топливо'),

            'plastic': pgettext_lazy('goods', 'Пластик'),

            'steel': pgettext_lazy('goods', 'Сталь'),

            'aluminium': pgettext_lazy('goods', 'Алюминий'),
        }
        # ------vvvvvvv------Оборудование на складе------vvvvvvv------
        equipments = {
            'medical': pgettext_lazy('goods', 'Медикаменты'),
            'drilling': pgettext_lazy('goods', 'Буровые установки'),
        }
        # ------vvvvvvv------Юниты на складе------vvvvvvv------
        units = {
            'rifle': pgettext_lazy('goods', 'Автоматы'),

            'tank': pgettext_lazy('goods', 'Танки'),
            'antitank': pgettext_lazy('goods', 'ПТ-орудия'),
            'station': pgettext_lazy('goods', 'Орбитальные орудия'),

            'jet': pgettext_lazy('goods', 'Штурмовики'),
            'pzrk': pgettext_lazy('goods', 'ПЗРК'),

            'ifv': pgettext_lazy('goods', 'БМП'),
            'mines': pgettext_lazy('goods', 'Мины'),

            'drone': pgettext_lazy('goods', 'БПЛА'),
        }

        # lock = GoodLock()
        # storage = Storage()

        for cat in ['minerals', 'oils', 'materials', 'equipments', 'units']:
            for good in locals().get(cat).keys():
                # lock.old_good = good
                Good.objects.filter(name=locals().get(cat)[good]).update(type=cat)

    dependencies = [
        ('storage', '0066_auto_20230715_1629'),
    ]

    operations = [
        migrations.RunPython(move_volumes),
    ]
