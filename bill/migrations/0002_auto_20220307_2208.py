# Generated by Django 3.1.3 on 2022-03-07 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changecoat',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='img/state_avatars/', verbose_name='Герб'),
        ),
        migrations.AlterModelTable(
            name='changecoat',
            table=None,
        ),
        migrations.AlterModelTable(
            name='changetaxes',
            table=None,
        ),
        migrations.AlterModelTable(
            name='changetitle',
            table=None,
        ),
        migrations.AlterModelTable(
            name='construction',
            table=None,
        ),
        migrations.AlterModelTable(
            name='exploreresources',
            table=None,
        ),
        migrations.AlterModelTable(
            name='purchaseauction',
            table=None,
        ),
    ]
