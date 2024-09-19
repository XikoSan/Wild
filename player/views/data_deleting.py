# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render


def data_deleting(request):
    return render(request, 'player/data_deleting.html', {})
