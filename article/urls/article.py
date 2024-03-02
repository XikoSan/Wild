# coding=utf-8
from django.conf.urls import url
from django.urls import path

from article.views.article_rated_list import article_rated_list
from article.views.article_rating import article_rating
from article.views.articles import articles
from article.views.create_article import create_article
from article.views.edit_article import edit_article
from article.views.new_article import new_article
from article.views.view_article import view_article
from article.views.vote_article import vote_article
from article.views.change_article import change_article

urlpatterns = [

    # страница статей
    url(r'^articles$', articles, name='articles'),

    # новая статья
    url(r'^new_article/$', new_article, name='new_article'),

    # создать статью
    url(r'^create_article/$', create_article, name='create_article'),

    # редактировать статью
    url(r'^edit_article/$', change_article, name='change_article'),

    # открытие статьи
    url(r'^article/(?P<pk>\d+)/$', view_article, name='view_article'),

    # редактирование статьи
    url(r'^article/(?P<pk>\d+)/edit/$', edit_article, name='edit_article'),

    # оценившие статью
    path('article/<str:pk>/<str:mode>/', article_rated_list, name='article_rated_list'),

    # голосовать за статью
    url(r'^vote_article/$', vote_article, name='vote_article'),

    # получить рейтинг статьи
    url(r'^article_rating/$', article_rating, name='article_rating'),
]
