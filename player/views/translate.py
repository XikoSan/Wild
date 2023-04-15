from player.player import Player
import os
import polib
from django.shortcuts import render
from django.http import HttpResponseRedirect
from wild_politics import settings
import gettext


def edit_translations(request, lang, context):
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
        po = polib.pofile(po_file_path)
        entries = []
        for entry in po:
            if entry.msgctxt == context or (not entry.msgctxt and 'None' == context):
                from player.logs.print_log import log
                log(entry.fuzzy)
                entries.append({
                    'msgid': entry.msgid,
                    'msgstr': entry.msgstr,
                    'fuzzy': entry.fuzzy
                })

        return render(request, 'player/translate.html', {'player': player, 'entries': entries, 'context': context})

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
