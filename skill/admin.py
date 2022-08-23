from django.contrib import admin
from skill.models.excavation import Excavation
from skill.models.finance import Finance
from skill.models.standardization import Standardization

class SkillAdmin(admin.ModelAdmin):
    list_display = ('player', 'level', 'max_level',)
    search_fields = ['player__nickname',]
    raw_id_fields = ('player',)

# Register your models here.
admin.site.register(Excavation, SkillAdmin)
admin.site.register(Finance, SkillAdmin)
admin.site.register(Standardization, SkillAdmin)