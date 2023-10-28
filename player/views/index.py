# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render
from datetime import datetime

def index(request):

    if request.user.is_authenticated:
        return redirect('overview')

    else:

        open_date_str = "2023-10-29 18:00:00"
        open_date = datetime.strptime(open_date_str, "%Y-%m-%d %H:%M:%S")

        is_open = False
        if datetime.now() > open_date:
            is_open = True

        lang = None
        language = request.LANGUAGE_CODE
        if language != 'ru':
            lang = 'en'

        return render(request, 'player/index.html', {
            'lang': lang,
            'is_open': is_open
        })
