from django.contrib import admin

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from party.primaries.primaries_leader import PrimariesLeader

# Register your models here.
admin.site.register(Party)
admin.site.register(PartyPosition)
admin.site.register(Primaries)
admin.site.register(PrimBulletin)
admin.site.register(PrimariesLeader)
admin.site.register(PartyApply)
admin.site.register(MembershipLog)
