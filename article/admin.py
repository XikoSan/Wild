from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django_summernote.admin import SummernoteModelAdmin

from article.models.article import Article
from article.models.comments_block import CommentsBlock
from article.models.subscription import Subscription


# Register your models here.
class ArticleAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    search_fields = ['player__nickname', 'title']

    list_display = ('title', 'player', 'date')
    ordering = ('-date',)

    summernote_fields = ('body',)

    raw_id_fields = ('player',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ['player__nickname', 'author__nickname']

    list_display = ('author', 'player', 'date')
    ordering = ('-date',)

    raw_id_fields = ('player', 'author',)


class CommentsBlockAdmin(admin.ModelAdmin):
    raw_id_fields = ('article',)


admin.site.register(Article, ArticleAdmin)
admin.site.register(CommentsBlock, CommentsBlockAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
