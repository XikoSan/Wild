# coding=utf-8
import os
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404

from player.player import Player


# Декоратор для проверки того, что:
#   1. Игрок от даного аккаунта существует
#   2. Этот игрок не забанен

# Декоратор получает на вход функцию
# В передающейся функции первым аргументом должен идти параметр request,
# а дальше произвольное кол-во аргументов
def check_player(func):
    # Создаем обёртывающую функцию для переданной func
    # Функция получает объект запроса - request(ведь, любое представление его получает)
    # и, если надо, переменное кол-во других аргументов, позиционных - *args и именованных - **kwargs
    def checking(request, *args, **kwargs):
        # Проходим все необходимые проверки:
        #                - - -
        # Если у игрока есть хоть один персонаж:
        if Player.objects.filter(account=request.user).exists():
            # Получаем игрока
            player = Player.objects.get(account=request.user)
            # Тут добавить УЗ суперов для обхода блокировки.
            if player.pk == 1 or request.user.is_staff:
                # Возвращение выполнения основной(переданной в check_player)
                # функции - func, с переданными ей аргументами - *args и **kwargs
                # player.increase_calc()
                return func(request, *args, **kwargs)
            else:
                # Получаем текущий ip игрока
                cur_ip = get_client_ip(request)
                # присваиваем ему этот адрес
                player.user_ip = cur_ip
                player.save()

                # проверка на IP работает только на продакшене
                if os.environ.get('PROD'):
                    # если найдены игроки с таким же ip как найденный, не считая самого игрока
                    if Player.objects.filter(user_ip=cur_ip).exclude(Q(pk=player.pk) | Q(banned=True)).exists():
                        players = Player.objects.filter(user_ip=cur_ip)
                        for it_player in players:
                            it_player.banned = True
                            it_player.save()
                        player.banned = True

                # Если игрок не забанен:
                if not player.banned:
                    # Возвращение выполнения основной(переданной в check_player)
                    # функции - func, с переданными ей аргументами - *args и **kwargs
                    # player.increase_calc()
                    return func(request, *args, **kwargs)
                # Если же забанен:
                else:
                    # Перенаправляем на страницу бана
                    return redirect('banned')
        # Если у игрока нет персонажей:
        else:
            # Пусть идет создавать нового
            return redirect('new_player')

    # Возвращаем проверяющую функцию
    return checking


# Получение IP игрока
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
