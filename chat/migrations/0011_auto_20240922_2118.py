# Generated by Django 3.2.18 on 2024-09-22 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_auto_20231008_0148'),
    ]

    operations = [
        migrations.AddField(
            model_name='stickerpack',
            name='creator_az',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_be',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_de',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_es',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_ind',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_lv',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_pl',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_pt_br',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_ru',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_tr',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='creator_uk',
            field=models.CharField(max_length=100, null=True, verbose_name='Автор набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_az',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_be',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_de',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_en',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_es',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_ind',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_lv',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_pl',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_pt_br',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_ru',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_tr',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='description_uk',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_az',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_be',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_de',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_es',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_ind',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_lv',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_pl',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_pt_br',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_ru',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_tr',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
        migrations.AddField(
            model_name='stickerpack',
            name='title_uk',
            field=models.CharField(max_length=100, null=True, verbose_name='Название набора'),
        ),
    ]
