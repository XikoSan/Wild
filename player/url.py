# coding=utf-8
from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from event.views.winter_festival import winter_festival
from player.views.banned import banned
from player.views.bonus_code.activate_code import activate_code
from player.views.bonus_code.bonus_code import bonus_code
from player.views.eula import eula
from player.views.game_event.halloween import halloween
from player.views.lists.damage_top import damage_top
from player.views.lists.region_players import region_players_list
from player.views.lists.world_online import world_online_list
from player.views.lists.world_players import world_players_list
from player.views.repost_reward import repost_reward
from player.views.skills.up_skill import up_skill
from player.views.translate.translate import edit_translations
from player.views.translate.translations import translations
from .views.answer_captcha import answer_captcha
from .views.buy_lootboxes import buy_lootboxes
from .views.change_back_allow import change_back_allow
from .views.change_bio import change_bio
from .views.change_nickname import change_nickname
from .views.change_wiki_hide_allow import change_wiki_hide_allow
from .views.claim_reward import claim_reward
from .views.color_change import color_change
from .views.comma_list import comma_list
from .views.dmg_tbl import dmg_tbl
from .views.expense_energy import expense_energy
from .views.full_auto_allow import full_auto_allow
from .views.game_event.new_year import new_year
from .views.game_event.summer import summer_festival
from .views.index import index
from .views.lists.cash_top import cash_top
from .views.lists.region_citizens import region_citizens_list
from .views.lists.skill_top import skill_top
from .views.my_profile import my_profile
from .views.new_player import new_player
from .views.no_social import no_social
from .views.open_lootboxes import open_lootboxes
from .views.overview import overview
from .views.set_language import set_language
from .views.set_timezone import set_timezone
from .views.skill_tbl import skill_tbl
from .views.view_profile import view_profile
from .views.wallet import wallet

urlpatterns = [

    # приветственная страница
    url(r'^$', index, name='index'),
    # ЕУЛА
    url(r'^eula$', eula, name='eula'),
    url(r'^dmg_tbl$', dmg_tbl, name='dmg_tbl'),
    url(r'^skill_tbl$', skill_tbl, name='skill_tbl'),
    # Соглашение об обработке ПД
    path('personal_data/', TemplateView.as_view(template_name='player/personal_data.html'), name='personal_data'),
    # регистрация нового персонажа
    url(r'^player/new/$', new_player, name='new_player'),
    # выход
    # url(r'^logout', logout.LogoutView.as_view(), name='logout'),

    # открытие списка всех игроков
    url(r'^world/players/', world_players_list, name='world_players_list'),
    # открытие списка всех игроков
    url(r'^world/online/', world_online_list, name='world_online_list'),
    # открытие списка населения региона
    url(r'^region/(?P<region_pk>\d+)/players/', region_players_list, name='region_players_list'),
    # открытие списка граждан региона
    url(r'^region/(?P<region_pk>\d+)/citizens/', region_citizens_list, name='region_citizens_list'),

    # список богатейших
    url(r'^cash_top/', cash_top, name='cash_top'),
    # списки лучших по характеристикам
    url(r'^skill_top/', skill_top, name='skill_top'),
    # список урона игрока
    url(r'^damage_top/', damage_top, name='damage_top'),

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
    # зимний фестиваль
    url(r'^winter_festival/$', winter_festival, name='winter_festival'),
    # летний фестиваль
    url(r'^summer_festival/$', summer_festival, name='summer_festival'),

    # контексты переводов
    path('translations/', translations, name='translations'),
    # переводы
    path('edit-translation/<str:lang>/<str:context>/', edit_translations, name='edit_translations'),

    # получение наград за обучение
    url(r'^claim_reward/$', claim_reward, name='claim_reward'),

    # открыть лутбоксы
    url(r'^open_lootboxes/$', open_lootboxes, name='open_lootboxes'),

    # купить лутбоксы
    url(r'^buy_lootboxes/$', buy_lootboxes, name='buy_lootboxes'),

    # ответ на капчу
    url(r'^answer_captcha', answer_captcha, name='answer_captcha'),

    # страница бонус-кода
    url(r'^bonus_code', bonus_code, name='bonus_code'),

    # активация бонус-кода
    url(r'^activate_code/', activate_code, name='activate_code'),
]
