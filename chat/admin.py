from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from .models import Chat, Message


class ChatAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(verbose_name='сообщения',
                                                                          is_stacked=False)},
    }


admin.site.register(Chat, ChatAdmin)


class MessageAdmin(admin.ModelAdmin):
    fields = [
        'author',
        'content',
        'timestamp',
    ]

    readonly_fields = ['timestamp', ]


admin.site.register(Message, MessageAdmin)
