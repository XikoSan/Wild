# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render


def index(request):

    if request.user.is_authenticated:
        return redirect('overview')

    else:
        lang = None
        language = request.LANGUAGE_CODE
        if language != 'ru':
            lang = 'en'

        return render(request, 'player/index.html', {
            'lang': lang
        })
