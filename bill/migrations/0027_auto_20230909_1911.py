# Generated by Django 3.1.3 on 2023-09-09 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0026_delete_geologicalsurveys'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseauction',
            old_name='good',
            new_name='old_good',
        ),
    ]
