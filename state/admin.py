from django.contrib import admin

from .parliament.bulletin import Bulletin
from .parliament.deputy_mandate import DeputyMandate
from .parliament.parliament import Parliament
from .parliament.parliament_party import ParliamentParty
from .parliament.parliament_voting import ParliamentVoting
from .state import State
from .treasury import Treasury

# Register your models here.
admin.site.register(State)
admin.site.register(Treasury)
admin.site.register(Parliament)
admin.site.register(ParliamentVoting)
admin.site.register(Bulletin)
admin.site.register(DeputyMandate)
admin.site.register(ParliamentParty)
