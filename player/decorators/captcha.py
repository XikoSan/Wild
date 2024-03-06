# coding=utf-8
import os
import random
import redis
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.utils import translation, timezone
from django.utils.translation import check_for_language
from django.utils.translation import ugettext as _

from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import JResponse
from datetime import timedelta

# Декоратор, перехватывающий запрашиваемую функцию,
# и возвращающий вместо неё Captcha,
# для предотвращения автоматизации

# для удобства использования игроками методы, экранированные этим тегом
# должны иметь соответствующе оформленный вызов со стороны JS

# Алгоритм:
# 1. Пользователь вызывает нужный POST запрос, параметры которого сохраняются
# 2. запрос попадает в Каптча-метод, в параметры пользователя записывается ответ на капчу
# 3. Метод вместо ответа возвращает задачку в всплывающем окне
# 4. Пользователь выбирает правильный вариант, он отправляется отдельным POST-запросом
# 5. Сервер возвращает успешность прохождения капчи
# 6. JS повторяет оригинальный запрос
def captcha(func):
    # Создаем обёртывающую функцию для переданной func
    # Функция получает объект запроса - request(ведь, любое представление его получает)
    # и, если надо, переменное кол-во других аргументов, позиционных - *args и именованных - **kwargs
    def checking(request, *args, **kwargs):
        # Проходим все необходимые проверки:
        # Если у игрока есть хоть один персонаж:
        if Player.objects.filter(account=request.user).exists():
            # Получаем игрока
            player = Player.objects.only('pk').get(account=request.user)

            # язык из настроек
            if PlayerSettings.objects.filter(player=player).exists():
                player_settings = PlayerSettings.objects.get(player=player)
            else:
                player_settings = PlayerSettings(player=player)

            # по умолчанию капча показывается в трети случаев
            captcha_proc = 30

            # за каждый час, прошедший со старой проверки, добавляется ещё 10%
            current_date = timezone.now()

            # если проходили капчу последние 15 минут - выходим
            if player_settings.captcha_date + timedelta(minutes=15) > timezone.now():
                return func(request, *args, **kwargs)

            time_difference = current_date - player_settings.captcha_date

            hours_passed = int(divmod(time_difference.total_seconds(), 3600)[0])
            term = hours_passed * 10

            if captcha_proc + term > 100:
                captcha_proc = 100
            else:
                captcha_proc = captcha_proc + term

            cap_check = random.choices([True, False, ], weights=[captcha_proc, 100 - captcha_proc, ])

            from player.logs.print_log import log

            if cap_check[0]:

                first_number = random.randint(1, 9)
                second_number = random.randint(1, 9)

                answer = first_number + second_number
                fail_answer = answer - random.randint(1, 9)

                left_answer = 0
                right_answer = 0
                # определяем, с какой стороны будет кнопка правильного ответа в попапе
                ch = random.choices([True, False, ], weights=[1, 1, ])

                if ch[0]:
                    left_answer = answer
                    right_answer = fail_answer
                else:
                    left_answer = fail_answer
                    right_answer = answer

                player_settings.captcha_ans = answer
                player_settings.save()

                data = {
                    'response': 'captcha',
                    'text': f'Выберите верный ответ: {first_number} + {second_number} = ',
                    'header': _('Пройдите Captcha'),
                    'white_btn': left_answer,
                    'grey_btn': right_answer,
                }
                return JResponse(data)

            # Возвращение выполнения основной функции
            else:
                return func(request, *args, **kwargs)


        # Если у игрока нет персонажей:
        else:
            # Пусть идет создавать нового
            return redirect('new_player')

    # Возвращаем проверяющую функцию
    return checking
