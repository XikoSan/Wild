from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.tasks import run_bill
from wild_politics.settings import JResponse
from article.models.article import Article
from article.models.subscription import Subscription
from django.utils.translation import pgettext

# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def subscription(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        try:
            author_pk = int(request.POST.get('pk'))

        except ValueError:
            data = {
                'header': pgettext('author_sub', 'Подписка'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('author_sub', 'ID автора должно быть целым числом'),
            }
            return JResponse(data)

        if Player.objects.filter(pk=author_pk).exists():
            # если подписка есть - удаляем
            if Subscription.objects.filter(
                                                author = Player.objects.get(pk=author_pk),
                                                player = player
                                            ).exists():
                Subscription.objects.filter(
                    author=Player.objects.get(pk=author_pk),
                    player=player
                ).delete()

            # иначе - создаем
            else:
                subs = Subscription(
                    author = Player.objects.get(pk=author_pk),
                    player = player
                )

                subs.save()

            data = {
                'response': 'ok',
            }
            return JResponse(data)

        else:
            data = {
                'response': pgettext('author_sub', 'Нет такого автора'),
                'header': pgettext('author_sub', 'Подписка'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('author_sub', 'Подписка'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
