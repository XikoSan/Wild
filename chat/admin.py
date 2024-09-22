from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from chat.models.messages.chat import Chat
from chat.models.messages.message_block import MessageBlock
from chat.models.messages.chat_members import ChatMembers

from chat.models.sticker import Sticker
from chat.models.sticker_pack import StickerPack
from chat.models.stickers_ownership import StickersOwnership
from modeltranslation.admin import TabbedTranslationAdmin


class StickerAdmin(admin.ModelAdmin):
    search_fields = ['description']
    list_display = ('get_pack_name', 'description')

    def get_pack_name(self, obj):
        return obj.pack.title


class StickerPackAdmin(TabbedTranslationAdmin):

    raw_id_fields = ('owner',)
    list_display = ('title', 'creator', 'price')


class StickersOwnershipAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname', 'pack__title']
    list_display = ('owner', 'pack')
    raw_id_fields = ('owner', 'pack')


class ChatMembersAdmin(admin.ModelAdmin):
    raw_id_fields = ('chat', 'player')


class MessageBlockAdmin(admin.ModelAdmin):
    raw_id_fields = ('chat',)


class ChatMembersInline(admin.TabularInline):
    model = ChatMembers


class ChatAdmin(admin.ModelAdmin):
    model = Chat
    inlines = [ChatMembersInline]


admin.site.register(Chat, ChatAdmin)
admin.site.register(MessageBlock, MessageBlockAdmin)
admin.site.register(ChatMembers, ChatMembersAdmin)

admin.site.register(StickerPack, StickerPackAdmin)
admin.site.register(StickersOwnership, StickersOwnershipAdmin)
admin.site.register(Sticker, StickerAdmin)
