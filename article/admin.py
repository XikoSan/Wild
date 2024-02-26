from django.contrib import admin

from article.models.article import Article
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.
class ArticleAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    search_fields = ['player__nickname', 'title']

    list_display = ('title', 'player', 'date')
    ordering = ('date',)

    summernote_fields = ('body',)

    raw_id_fields = ('player',)


admin.site.register(Article, ArticleAdmin)
