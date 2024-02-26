# coding=utf-8
from django.conf.urls import url
from django.urls import path

from article.views.articles import articles
from article.views.view_article import view_article
from article.views.new_article import new_article

urlpatterns = [

    # страница статей
    url(r'^articles$', articles, name='articles'),

    # открытие статьи
    url(r'^new_article/$', new_article, name='new_article'),

    # открытие статьи
    url(r'^article/(?P<pk>\d+)/$', view_article, name='view_article'),
]
