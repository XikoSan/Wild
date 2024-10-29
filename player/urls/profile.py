# coding=utf-8
from django.conf.urls import url

from player.views.customization.avatar_edit import avatar_edit

urlpatterns = [

    # редактировать аватар
    url(r'^avatar_edit/$', avatar_edit, name='avatar_edit'),
]
