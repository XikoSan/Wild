from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models

from gov.models.minister import Minister
from gov.models.minister_right import MinisterRight
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.vote import Vote


class PresidentialVotingAdmin(admin.ModelAdmin):
    list_filter = ("running",)

    raw_id_fields = ('president',)

    list_display = ['get_obj_name', 'running', 'voting_start', ]

    def get_obj_name(self, obj):
        return obj.president.state.title

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Кандидаты',
            is_stacked=False
        )},
    }


class PresidentAdmin(admin.ModelAdmin):
    search_fields = ['state', 'leader']

    raw_id_fields = ('state', 'leader',)

    list_display = ['state', 'leader', ]


class MinisterRightAdmin(admin.ModelAdmin):
    search_fields = ['right']

    list_display = ['right', ]


class MinisterAdmin(admin.ModelAdmin):
    search_fields = ['state', 'player']

    raw_id_fields = ('state', 'player',)

    list_display = ['state', 'player', ]

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple(
            verbose_name='Права',
            is_stacked=False
        )},
    }


# Register your models here.
admin.site.register(Vote)
admin.site.register(PresidentialVoting, PresidentialVotingAdmin)
admin.site.register(President, PresidentAdmin)
admin.site.register(Minister, MinisterAdmin)
admin.site.register(MinisterRight, MinisterRightAdmin)
