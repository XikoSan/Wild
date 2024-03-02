from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django_summernote.admin import SummernoteModelAdmin

from article.models.article import Article


# Register your models here.
class ArticleAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    search_fields = ['player__nickname', 'title']

    list_display = ('title', 'player', 'date')
    ordering = ('date',)

    summernote_fields = ('body',)

    raw_id_fields = ('player',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


admin.site.register(Article, ArticleAdmin)
