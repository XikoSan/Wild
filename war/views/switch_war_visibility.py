import re
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.get_subclasses import get_subclasses
from war.models.wars.player_damage import PlayerDamage
from war.models.wars.war import War
from wild_politics.settings import JResponse
from django.contrib.contenttypes.models import ContentType


# скрыть войну из списка
@login_required(login_url='/')
@check_player
def switch_war_visibility(request):
    if request.method == "POST":
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        war_types = get_subclasses(War)

        class_founded = False
        war_class = None

        for war_type in war_types:
            if war_type.__name__ == request.POST.get('war_type'):
                class_founded = True
                war_class = war_type
                break

        if not class_founded:
            data = {
                'response': pgettext('war_visibility', 'Нет такого типа войн'),
                'header': pgettext('war_visibility', 'Скрытие войны'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if not war_class.objects.filter(pk=int(request.POST.get('pk'))).exists():
            data = {
                'response': pgettext('war_visibility', 'Нет такой войны'),
                'header': pgettext('war_visibility', 'Скрытие войны'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        war_obj = war_class.objects.get(pk=int(request.POST.get('pk')))

        war_content_type = ContentType.objects.get_for_model(war_obj)

        if not PlayerDamage.objects.filter(
                                            content_type=war_content_type,
                                            object_id=war_obj.pk,
                                           player=player,
                                           side=request.POST.get('side')).exists():
            data = {
                'response': pgettext('war_visibility', 'Нет такой записи об участии в бою'),
                'header': pgettext('war_visibility', 'Скрытие войны'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        pd = PlayerDamage.objects.get(
                                        content_type=war_content_type,
                                        object_id=war_obj.pk,
                                        player=player, side=request.POST.get('side')
                                    )

        if pd.hide:
            pd.hide = False

        else:
            pd.hide = True

        pd.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('war_visibility', 'Скрытие войны'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
