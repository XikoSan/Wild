# Generated by Django 3.1.3 on 2023-09-10 21:14

from django.db import migrations
from django.utils.translation import gettext_lazy, pgettext_lazy, pgettext, ugettext as _


class Migration(migrations.Migration):

    def move_schemas(apps, schema_editor):

        Blueprint = apps.get_model('factory', 'Blueprint')
        Component = apps.get_model('factory', 'Component')

        Good = apps.get_model('storage', 'Good')

        tovary = {
            # Уголь
            'coal': pgettext_lazy('goods', 'Уголь'),
            # Железо
            'iron': pgettext_lazy('goods', 'Железо'),
            # Бокситы
            'bauxite': pgettext_lazy('goods', 'Бокситы'),

            'wti_oil': pgettext_lazy('goods', 'Нефть WTI'),

            'brent_oil': pgettext_lazy('goods', 'Нефть Brent'),

            'urals_oil': pgettext_lazy('goods', 'Нефть Urals'),

            'gas': pgettext_lazy('goods', 'Бензин'),

            'diesel': pgettext_lazy('goods', 'Дизельное топливо'),

            'plastic': pgettext_lazy('goods', 'Пластик'),

            'steel': pgettext_lazy('goods', 'Сталь'),

            'aluminium': pgettext_lazy('goods', 'Алюминий'),

            'medical': pgettext_lazy('goods', 'Медикаменты'),
            'drilling': pgettext_lazy('goods', 'Буровые установки'),

            'rifle': pgettext_lazy('goods', 'Автоматы'),

            'tank': pgettext_lazy('goods', 'Танки'),
            'antitank': pgettext_lazy('goods', 'ПТ-орудия'),
            'station': pgettext_lazy('goods', 'Орбитальные орудия'),

            'jet': pgettext_lazy('goods', 'Штурмовики'),
            'pzrk': pgettext_lazy('goods', 'ПЗРК'),

            'ifv': pgettext_lazy('goods', 'БМП'),
            'mines': pgettext_lazy('goods', 'Мины'),

            'drone': pgettext_lazy('goods', 'Дроны'),
        }

        gas = {
            'title': pgettext('goods', 'Бензин'),
            # 'title': pgettext('goods', 'gas'),

            'resources':
                [
                    {
                        'cash': 5,
                        'wti_oil': 10,
                    },
                    {
                        'cash': 8,
                        'brent_oil': 15,
                    },
                    {
                        'cash': 8,
                        'urals_oil': 15,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        plastic = {
            'title': pgettext('goods', 'Пластик'),
            # 'title': pgettext('goods', 'plastic'),

            'resources':
                [
                    {
                        'cash': 8,
                        'wti_oil': 15,
                    },
                    {
                        'cash': 5,
                        'brent_oil': 10,
                    },
                    {
                        'cash': 8,
                        'urals_oil': 15,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        diesel = {
            'title': pgettext('goods', 'Дизель'),
            # 'title': pgettext('goods', 'plastic'),

            'resources':
                [
                    {
                        'cash': 8,
                        'wti_oil': 15,
                    },
                    {
                        'cash': 8,
                        'brent_oil': 15,
                    },
                    {
                        'cash': 5,
                        'urals_oil': 10,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        steel = {
            'title': pgettext('goods', 'Сталь'),

            'resources':
                [
                    {
                        'cash': 5,
                        'coal': 5,
                        'iron': 10,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        aluminium = {
            'title': pgettext('goods', 'Алюминий'),

            'resources':
                [
                    {
                        'cash': 10,
                        'bauxite': 10,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        medical = {
            'title': pgettext('goods', 'Медикаменты'),

            'resources':
                [
                    {
                        'cash': 25,
                        'plastic': 5,
                        'steel': 2,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        drilling = {
            'title': pgettext('goods', 'Буровые установки'),

            'resources':
                [
                    {
                        'cash': 50,
                        'aluminium': 10,
                        'steel': 1,
                    },
                ],

            'time': 10,
            'energy': 2,
        }
        rifle = {
            'title': pgettext('goods', 'Автоматы'),

            'resources':
                [
                    {
                        'cash': 10,
                        'steel': 1,
                    },
                ],

            'time': 3,
            'energy': 1,
        }
        tank = {
            'title': pgettext('goods', 'Танки'),

            'resources':
                [
                    {
                        'cash': 100,
                        'gas': 5,
                        'steel': 15,
                    },
                    {
                        'cash': 80,
                        'diesel': 5,
                        'steel': 18,
                    },
                ],

            'time': 30,
            'energy': 1,
        }
        jet = {
            'title': pgettext('goods', 'Штурмовики'),

            'resources':
                [
                    {
                        'cash': 150,
                        'aluminium': 15,
                        'gas': 5,
                    },
                ],

            'time': 45,
            'energy': 1,
        }
        pzrk = {
            'title': pgettext('goods', 'ПЗРК'),

            'resources':
                [
                    {
                        'cash': 30,
                        'gas': 5,
                        'steel': 2,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        antitank = {
            'title': pgettext('goods', 'ПТ-орудия'),

            'resources':
                [
                    {
                        'cash': 30,
                        'gas': 2,
                        'steel': 2,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        mines = {
            'title': pgettext('goods', 'Мины'),

            'resources':
                [
                    {
                        'cash': 20,
                        'aluminium': 1,
                        'steel': 2,
                    },
                ],

            'time': 10,
            'energy': 1,
        }
        ifv = {
            'title': pgettext('goods', 'БМП'),

            'resources':
                [
                    {
                        'cash': 50,
                        'diesel': 5,
                        'steel': 5,
                    },
                ],

            'time': 10,
            'energy': 2,
        }
        drone = {
            'title': pgettext('goods', 'БПЛА'),

            'resources':
                [
                    {
                        'cash': 10,
                        'gas': 1,
                        'aluminium': 5,
                    },
                ],

            'time': 10,
            'energy': 2,
        }
        # -------------^^^^^^^---------------Производственные схемы---------------^^^^^^^---------------
        schemas = (
            ('gas', gas.get('title')),
            ('diesel', diesel.get('title')),
            ('plastic', plastic.get('title')),

            ('steel', steel.get('title')),
            ('aluminium', aluminium.get('title')),

            ('medical', medical.get('title')),
            ('drilling', drilling.get('title')),

            ('rifle', rifle.get('title')),
            ('tank', tank.get('title')),
            ('jet', jet.get('title')),
            ('pzrk', pzrk.get('title')),
            ('antitank', antitank.get('title')),
            ('mines', mines.get('title')),
            ('ifv', ifv.get('title')),
            ('drone', drone.get('title')),
        )

        for good in schemas:

            product = locals().get(good[0])

            index = 0

            for vari in product.get('resources'):

                from player.logs.print_log import log
                log(product.get('title'))

                bp = Blueprint(
                    good=Good.objects.get(name_ru=locals().get('tovary')[good[0]]),
                    energy_cost=product.get('energy'),
                    cash_cost=product.get('resources')[index].get('cash'),
                )
                bp.save()

                for source in product.get('resources')[index].keys():

                    if source == 'cash':
                        continue

                    good_comp = Good.objects.get(name_ru=locals().get('tovary')[source])

                    comp = Component(
                        blueprint=bp,
                        good=good_comp,
                        count=product.get('resources')[index].get(source)
                    )
                    comp.save()

                index += 1

    dependencies = [
        ('factory', '0022_auto_20230910_2311'),
    ]

    operations = [
        migrations.RunPython(move_schemas),
    ]
