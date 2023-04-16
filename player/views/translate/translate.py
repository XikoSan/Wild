from player.player import Player
import os
import polib
from django.shortcuts import render
from django.http import HttpResponseRedirect
from wild_politics import settings
from django.utils.translation import get_language_info
import gettext
from django.shortcuts import redirect


def edit_translations(request, lang, context):

    groups = list(request.user.groups.all().values_list('name', flat=True))

    if not request.user.is_superuser and 'translator' not in groups:
        return redirect('overview')

    player = Player.get_instance(account=request.user)

    if lang == 'ru':
        lang = 'en'

    domain = 'django'
    po_file_path = os.path.join(settings.BASE_DIR, 'locale', lang, 'LC_MESSAGES', '{}.po'.format(domain))

    if not context:
        context = request.POST.get('context')

    if request.method == 'POST':
        # Принимаем данные из формы и сохраняем их в файл перевода
        form_data = request.POST.dict()
        del form_data['csrfmiddlewaretoken']  # Удаляем токен CSRF
        save_translation_file(po_file_path, form_data, context, player)

        rebuild_mo_file = request.POST.get('rebuild_mo_file')

        if rebuild_mo_file and request.user.is_superuser:

            mo_file_path = os.path.join(settings.BASE_DIR, 'locale', lang, 'LC_MESSAGES', '{}.mo'.format(domain))
            if os.path.exists(mo_file_path):
                os.remove(mo_file_path)

            # Собираем MO-файл, если была выбрана опция "Собрать MO-файл"
            po = polib.pofile(po_file_path)

            mo_file_path = os.path.join(settings.BASE_DIR, 'locale', lang, 'LC_MESSAGES', '{}.mo'.format(domain))
            po.save_as_mofile(mo_file_path)

        # Перенаправляем на эту же страницу, чтобы обновить данные
        return HttpResponseRedirect(request.path_info)

    else:
        if not os.path.isfile(po_file_path):
            return redirect('overview')

        po = polib.pofile(po_file_path)
        entries = []
        for entry in po:
            if entry.msgctxt == context or (not entry.msgctxt and 'None' == context):
                entries.append({
                    'msgid': entry.msgid,
                    'msgstr': entry.msgstr,
                    'fuzzy': entry.fuzzy
                })

        return render(request, 'player/translate/translate.html', {'player': player,
                                                                   'entries': entries,
                                                                   'context': context,
                                                                   'locale': get_language_info(lang)['name_local']
                                                                   })

def save_translation_file(file_path, data, context, player):

    # Загружаем файл с помощью polib и обновляем переводы
    po = polib.pofile(file_path)

    # log(data)
    for entry in po:
        if entry.msgid in data and entry.msgstr != data.get(entry.msgid):
            if entry.msgctxt == context or (not entry.msgctxt and 'None' == context):  # если контекст совпадает, то обновим msgstr
                entry.fuzzy = False
                entry.msgstr = data.get(entry.msgid)
                # добавляем комментарий с именем пользователя
                entry.comment = gettext.gettext(f'Last modified by {player.nickname}, id {player.pk}')

    po.save()
