from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from polls.models.poll import Poll
from polls.models.variant import Variant


class PollAdmin(admin.ModelAdmin):
    search_fields = ['header']
    list_display = ('header', 'poll_dtime')


class VariantAdmin(admin.ModelAdmin):
    raw_id_fields = ('poll',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Голоса',
            is_stacked=False
        )},
    }


# Register your models here.
admin.site.register(Poll, PollAdmin)
admin.site.register(Variant, VariantAdmin)
