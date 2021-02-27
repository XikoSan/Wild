from django.contrib import admin

from storage.models.destroy import Destroy
from storage.models.storage import Storage
from storage.models.transport import Transport

# Register your models here.
admin.site.register(Storage)
admin.site.register(Transport)
admin.site.register(Destroy)
