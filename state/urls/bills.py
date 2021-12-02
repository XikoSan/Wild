# coding=utf-8
from django.conf.urls import url

from state.views.bills.new_bill import new_bill
from state.views.bills.vote_bill import vote_bill

urlpatterns = [

    # отправить законопроект:
    url(r'^new_bill/$', new_bill, name='new_bill'),
    # проголосовать за законопроект
    url(r'^vote_bill/$', vote_bill, name='vote_bill'),
]
