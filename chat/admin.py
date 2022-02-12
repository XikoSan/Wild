from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from chat.models.models import Chat, Message
from chat.models.sticker import Sticker
from chat.models.sticker_pack import StickerPack
from chat.models.stickers_ownership import StickersOwnership


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


class StickerAdmin(admin.ModelAdmin):
    search_fields = ['description']
    list_display = ('get_pack_name', 'description')

    def get_pack_name(self, obj):
        return obj.pack.title


class StickersOwnershipAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname', 'pack__title']
    list_display = ('owner', 'pack')
    raw_id_fields = ('owner', 'pack')


admin.site.register(Message, MessageAdmin)
admin.site.register(StickerPack)
admin.site.register(StickersOwnership, StickersOwnershipAdmin)
admin.site.register(Sticker, StickerAdmin)
