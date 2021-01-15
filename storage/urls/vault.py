# coding=utf-8
from django.conf.urls import include, url

from storage.views.vault.produce_energy import produce_energy

urlpatterns = [

    # производство энергии:
    url(r'^produce_energy/$', produce_energy, name='produce_energy'),
]
