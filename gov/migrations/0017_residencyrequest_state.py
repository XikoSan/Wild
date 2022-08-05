# Generated by Django 3.1.3 on 2022-08-05 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('state', '0039_state_residency'),
        ('gov', '0016_remove_residencyrequest_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='residencyrequest',
            name='state',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, related_name='req_state', to='state.state', verbose_name='Государство'),
            preserve_default=False,
        ),
    ]
