from django.contrib.auth.decorators import login_required

from party.party import Party
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# проголосовать на праймериз
@login_required(login_url='/')
@check_player
def vote_primaries(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        from player.logs.print_log import log
        log(request.POST.get('party_pk'))

        try:
            party_pk = int(request.POST.get('party_pk'))

        except ValueError:
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'ID партии должен быть целым числом'),
            }
            return JResponse(data)

        # если игрок НЕ состоит в партии, на праймериз которой голосует
        if not player.party == Party.objects.get(pk=party_pk):
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Вы не состоите в этой партии'),
            }
            return JResponse(data)

        # если нет активных праймериз
        if not Primaries.objects.filter(party=Party.objects.get(pk=party_pk), running=True).exists():
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Активных праймериз нет'),
            }
            return JResponse(data)

        # если игрок ещё уже голосовал
        if PrimBulletin.objects.filter(
                primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True),
                player=player).exists():
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Вы уже голосовали'),
            }
            return JResponse(data)

        try:
            player_pk = int(request.POST.get('player_pk'))

        except ValueError:
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Нельзя голосовать за себя'),
            }
            return JResponse(data)

        # если игрок = кандидат
        if player.pk == player_pk:
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Нельзя голосовать за себя'),
            }
            return JResponse(data)

        # если такого игрока нет в партии
        if not Player.objects.filter(pk=player_pk, party=party_pk).exists():
            data = {
                'header': pgettext('vote_primaries', 'Голосование на праймериз'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('vote_primaries', 'Такого кандидата в партии нет'),
            }
            return JResponse(data)

        # создаем новый бюллетень голосования за переданного игрока
        vote = PrimBulletin(primaries=Primaries.objects.get(party=Party.objects.get(pk=party_pk), running=True),
                            player=player,
                            candidate=Player.get_instance(pk=player_pk))
        # сохраняем бюллетень
        vote.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('vote_primaries', 'Голосование на праймериз'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
