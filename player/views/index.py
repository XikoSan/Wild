# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render


def index(request):
    if request.user.is_authenticated:
        return redirect('overview')
    else:
        return render(request, 'player/index.html', {})