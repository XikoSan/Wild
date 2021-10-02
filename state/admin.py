from django.contrib import admin

from state.models.parliament.bulletin import Bulletin
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.parliament.parliament_voting import ParliamentVoting
from state.models.state import State
from state.models.treasury import Treasury

# Register your models here.
admin.site.register(State)
admin.site.register(Treasury)
admin.site.register(Parliament)
admin.site.register(ParliamentVoting)
admin.site.register(Bulletin)
admin.site.register(DeputyMandate)
admin.site.register(ParliamentParty)
