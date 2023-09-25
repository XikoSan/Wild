from django.db import migrations
from django.utils import translation
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _


class Migration(migrations.Migration):

    def set_typesize(apps, schema_editor):
        Good = apps.get_model('storage', 'Good')

        # ------vvvvvvv------Все типы товаров------vvvvvvv------
        goods = {
            'cash': pgettext_lazy('goods', 'Наличные'),

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

            'drone': pgettext_lazy('goods', 'БПЛА'),
        }

        sizes = {
            'large': ['coal', 'iron', 'bauxite', 'wti_oil', 'brent_oil', 'urals_oil'],
            'medium': ['gas', 'diesel', 'plastic', 'steel', 'aluminium', 'medical', 'rifle'],
            'small': ['tank', 'mines', 'antitank', 'jet', 'pzrk', 'ifv', 'drone', 'drilling'],
        }

        for good in Good.objects.all():
            for size in locals().get('sizes').keys():
                for mat_key in locals().get('sizes')[size]:

                    translation.activate('ru')

                    if locals().get('goods')[mat_key] == good.name_ru:
                        good.size = size

                        translation.activate('en')

                        good.name_en = locals().get('goods')[mat_key]

                        good.save()

    dependencies = [
        ('storage', '0074_auto_20230914_2242'),
    ]

    operations = [
        migrations.RunPython(set_typesize),
    ]
