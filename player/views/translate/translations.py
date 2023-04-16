from player.player import Player
import os
import polib
from django.shortcuts import render
from django.http import HttpResponseRedirect
from wild_politics import settings
from django.utils.translation import get_language_info
from django.utils.translation import get_language_from_request
from django.utils.translation import get_language
import gettext
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from player.decorators.player import check_player


@login_required(login_url='/')
@check_player
def translations(request):

    user_language = get_language()

    groups = list(request.user.groups.all().values_list('name', flat=True))

    if not request.user.is_superuser and 'translator' not in groups:
        return redirect('overview')

    player = Player.get_instance(account=request.user)

    po_file_path = os.path.join(settings.BASE_DIR, 'locale', 'en', 'LC_MESSAGES', '{}.po'.format('django'))

    po = polib.pofile(po_file_path)

    context_list = []
    for entry in po:
        if entry.msgctxt not in context_list:
            context_list.append(entry.msgctxt)

    languages_dict = {}
    for lang in settings.LANGUAGES:
        languages_dict[lang[0]] = get_language_info(lang[0])['name_local']

    if user_language == 'ru':
        user_language = 'en'


    return render(request, 'player/translate/translations.html', {'player': player,
                                                                   'context_list': context_list,
                                                                   'languages_dict': languages_dict,
                                                                   'user_language': user_language,
                                                               })
