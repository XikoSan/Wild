from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from ava_border.models.ava_border import AvaBorder
from ava_border.models.ava_border_ownership import AvaBorderOwnership


class AvaBorderAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']
    list_display = ('title', 'price', 'description')


class AvaBorderOwnershipAdmin(admin.ModelAdmin):
    search_fields = ['owner__nickname', 'border__title']
    list_display = ('owner', 'border', 'in_use')
    raw_id_fields = ('owner', 'border')


admin.site.register(AvaBorderOwnership, AvaBorderOwnershipAdmin)
admin.site.register(AvaBorder, AvaBorderAdmin)
