# coding=utf-8
from django.conf.urls import url

from player.views.banned import banned
from player.views.eula import eula
from player.views.game_event.halloween import halloween
from player.views.lists.region_players import region_players_list
from player.views.lists.world_players import world_players_list
from player.views.repost_reward import repost_reward
from player.views.skills.up_skill import up_skill
from .views.change_back_allow import change_back_allow
from .views.change_bio import change_bio
from .views.change_nickname import change_nickname
from .views.change_wiki_hide_allow import change_wiki_hide_allow
from .views.color_change import color_change
from .views.comma_list import comma_list
from .views.expense_energy import expense_energy
from .views.full_auto_allow import full_auto_allow
from .views.game_event.new_year import new_year
from .views.index import index
from .views.lists.cash_top import cash_top
from .views.lists.region_citizens import region_citizens_list
from .views.lists.skill_top import skill_top
from .views.my_profile import my_profile
from .views.new_player import new_player
from .views.no_social import no_social
from .views.overview import overview
from .views.set_language import set_language
from .views.set_timezone import set_timezone
from .views.view_profile import view_profile
from .views.wallet import wallet

from player.views.translate.translate import edit_translations
from django.urls import path

urlpatterns = [

    # приветственная страница
    url(r'^$', index, name='index'),
    # ЕУЛА
    url(r'^eula$', eula, name='eula'),
    # регистрация нового персонажа
    url(r'^player/new/$', new_player, name='new_player'),
    # выход
    # url(r'^logout', logout.LogoutView.as_view(), name='logout'),

    # открытие списка всех игроков
    url(r'^world/players/', world_players_list, name='world_players_list'),
    # открытие списка населения региона
    url(r'^region/(?P<region_pk>\d+)/players/', region_players_list, name='region_players_list'),
    # открытие списка граждан региона
    url(r'^region/(?P<region_pk>\d+)/citizens/', region_citizens_list, name='region_citizens_list'),

    # список богатейших
    url(r'^cash_top/', cash_top, name='cash_top'),
    # списки лучших по характеристикам
    url(r'^skill_top/', skill_top, name='skill_top'),

    # открытие "обзора"
    url(r'^overview$', overview, name='overview'),
    # пополнение энергии:
    url(r'^recharge/$', expense_energy, name='expense_energy'),

    # открытие страницы персонажа игрока
    url(r'^profile/$', my_profile, name='my_profile'),
    # изменить никнейм
    url(r'^change_nickname/$', change_nickname, name='change_nickname'),

    # изменить биографию
    url(r'^change_bio/$', change_bio, name='change_bio'),

    # бан по списку вычисленных айди
    url(r'^comma_list/$', comma_list, name='comma_list'),

    # изменить язык игры
    url(r'^set_lang', set_language, name='set_lang'),

    # изменить часовой пояс игры
    url(r'^set_tz', set_timezone, name='set_tz'),

    # изменить цвета игры
    url(r'^color_change', color_change, name='color_change'),

    # смена отображения партийного аватара
    url(r'^change_back_allow', change_back_allow, name='change_back_allow'),

    # использовать Энергетики в авто-добыче
    url(r'^full_auto_allow', full_auto_allow, name='full_auto_allow'),

    # Скрыть кнопку Wiki
    url(r'^wiki_hide_allow', change_wiki_hide_allow, name='change_wiki_hide_allow'),

    # Начать учёт активностей
    url(r'^reward_4_repost', repost_reward, name='reward_4_repost'),

    # Открытие профиля персонажа для просмотра(другими игроками)
    url(r'^profile/(?P<pk>\d+)/$', view_profile, name='view_profile'),

    # открытие страницы кошелька
    url(r'^wallet/$', wallet, name='wallet'),

    # Открытие страницы забаненного игрока
    url(r'^banned/$', banned, name='banned'),

    # удаление аккаунтов, не имеющих соцсеть
    url(r'^no_social/$', no_social, name='no_social'),

    # хэллоуинский ивент
    url(r'^halloween/$', halloween, name='halloween'),
    # новый год
    url(r'^new_year/$', new_year, name='new_year'),


    # переводы
    path('edit-translation/<str:lang>/<str:context>/', edit_translations, name='edit_translations'),
]
