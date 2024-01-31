# coding=utf-8
from django.conf.urls import url

from bill.views.bills.speedup_bill import speedup_bill
from bill.views.bills.cancel_bill import cancel_bill
from bill.views.bills.new_bill import new_bill
from bill.views.bills.vote_bill import vote_bill

urlpatterns = [

    # отправить законопроект:
    url(r'^new_bill/$', new_bill, name='new_bill'),
    # проголосовать за законопроект
    url(r'^vote_bill/$', vote_bill, name='vote_bill'),
    # министр: ускорить законопроект
    url(r'^speedup_bill/$', speedup_bill, name='speedup_bill'),
    # отменить законопроект
    url(r'^cancel_bill/$', cancel_bill, name='cancel_bill'),
]
