from PIL import Image
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.utils.translation import pgettext
from io import BytesIO

from player.decorators.player import check_player
from player.forms import ImageForm
from player.logs.gold_log import GoldLog
from player.player import Player
from wild_politics.settings import JResponse


@login_required(login_url='/')
@check_player
def avatar_edit(request):
    player = Player.get_instance(account=request.user)

    if request.method == 'POST':
        if player.image and player.gold < 100:
            return redirect('my_profile')

        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            if player.image:
                player.gold -= 100
                gold_log = GoldLog(player=player, gold=-100, activity_txt='avatar')
                gold_log.save()

            player.image = form.cleaned_data['image']
            player.save()

            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            w = form.cleaned_data['width']
            h = form.cleaned_data['height']

            image = Image.open(player.image.path)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            webp_image_path = f'img/avatars/{player.id}_{timestamp}.webp'
            resized_image.save(player.image.storage.path(webp_image_path), 'WEBP', quality=85)
            player.image.name = webp_image_path
            player.save()

            # Создаем уменьшенные изображения
            image_75 = resized_image.resize((75, 75), Image.ANTIALIAS)
            img_io_75 = BytesIO()
            image_75.save(img_io_75, format='WEBP', quality=85)
            player.image_75.save(f"{player.id}_{timestamp}.webp", ContentFile(img_io_75.getvalue()), save=False)

            image_33 = resized_image.resize((33, 33), Image.ANTIALIAS)
            img_io_33 = BytesIO()
            image_33.save(img_io_33, format='WEBP', quality=85)
            player.image_33.save(f"{player.id}_{timestamp}.webp", ContentFile(img_io_33.getvalue()), save=False)

            player.save()

            data = {'response': 'ok'}
            return JResponse(data)

        else:
            data = {
                'response': pgettext('change_nickname', 'Форма смены аватара недействительна'),
                'header': pgettext('change_nickname', 'Смена аватара'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('change_nickname', 'Смена аватара'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
