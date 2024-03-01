# coding=utf-8
from django.conf.urls import url
from django.urls import path

from article.views.articles import articles
from article.views.create_article import create_article
from article.views.new_article import new_article
from article.views.view_article import view_article

urlpatterns = [

    # страница статей
    url(r'^articles$', articles, name='articles'),

    # новая статья
    url(r'^new_article/$', new_article, name='new_article'),

    # создать статью
    url(r'^create_article/$', create_article, name='create_article'),

    # открытие статьи
    url(r'^article/(?P<pk>\d+)/$', view_article, name='view_article'),
]
