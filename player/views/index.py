# coding=utf-8

from django.shortcuts import redirect
from django.shortcuts import render
from datetime import datetime
from django.utils import translation
from django.conf import settings

def index(request):

    if request.user.is_authenticated:
        return redirect('overview')

    else:

        open_date_str = "2023-10-29 18:00:00"
        open_date = datetime.strptime(open_date_str, "%Y-%m-%d %H:%M:%S")

        is_open = False
        if datetime.now() > open_date:
            is_open = True

        from player.logs.print_log import log
        log(request.LANGUAGE_CODE)

        lang = None
        language = request.LANGUAGE_CODE
        if language != 'ru':
            lang = 'en'
            translation.activate(lang)

        log(lang)

        # Формируем ответ с рендерингом шаблона
        response = render(request, 'player/index.html', {
            'lang': lang,
            'is_open': is_open
        })

        # Устанавливаем cookie для языка, если он не 'ru'
        if language != 'ru':
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, 'en', max_age=30 * 24 * 60 * 60)  # Cookie на 30 дней

        return response