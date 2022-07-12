# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render


def eula(request):
    return render(request, 'player/eula.html', {})
