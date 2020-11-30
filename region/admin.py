from django.contrib import admin

from region.region import Region
from region.neighbours import Neighbours

# Register your models here.
admin.site.register(Region)
admin.site.register(Neighbours)
