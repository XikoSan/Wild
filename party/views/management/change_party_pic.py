from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from PIL import Image
from player.decorators.player import check_player
from player.player import Player
from party.forms import ImageForm
from party.forms import MembersImageForm
from wild_politics.settings import JResponse

# изменение описания партии
@login_required(login_url='/')
@check_player
def change_party_pic(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        # если игрок действительно лидер партии
        if player.party_post.party_lead:

            form = None
            mode = request.POST.get('img_mode')

            if int(mode) == 1:
                form = ImageForm(request.POST, request.FILES)

            elif int(mode) == 2:
                form = MembersImageForm(request.POST, request.FILES)

            else:
                return HttpResponse('Ошибка варианта формы', content_type='text/html')

            if form.is_valid():
                mode_field = None

                if int(mode) == 1:
                    mode_field = 'image'
                elif int(mode) == 2:
                    mode_field = 'members_image'

                setattr(player.party, mode_field, form.cleaned_data[mode_field])
                player.party.save()

                x = form.cleaned_data['x']
                y = form.cleaned_data['y']
                w = form.cleaned_data['width']
                h = form.cleaned_data['height']

                image = Image.open(getattr(player.party, mode_field))

                cropped_image = image.crop((x, y, w + x, h + y))
                resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)
                resized_image.save(getattr(player.party, mode_field).path)

                data = {
                    'response': 'ok',
                }
                return JResponse(data)

            else:
                return HttpResponse('Ошибка формы', content_type='text/html')

        else:
            return HttpResponse('У вас недостаточно прав!', content_type='text/html')

    # если страницу только грузят
    else:
        return HttpResponse('Ты уверен что тебе сюда, путник?', content_type='text/html')
