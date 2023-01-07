import pytz
import redis
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from party.logs.party_apply import PartyApply
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import TIME_ZONE


@login_required(login_url='/')
@check_player
# Opening page with selected party data
def open_party(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)

    party = get_object_or_404(Party, pk=pk)

    party_characters = Player.objects.only('pk', 'party').filter(party=party)

    online_dict = {}

    if party_characters:
        r = redis.StrictRedis(host='redis', port=6379, db=0)

        for char in party_characters:
            timestamp = r.hget('online', str(char.pk))
            if timestamp:
                online_dict[char.pk] = datetime.fromtimestamp(int(timestamp)).replace(
                    tzinfo=pytz.timezone(TIME_ZONE)).astimezone(
                    tz=pytz.timezone(player.time_zone)).strftime("%d.%m.%Y")

    return render(request, 'party/party_view.html', {
        'page_name': party.title,
        'player': player,
        'party': party,

        'has_request': PartyApply.objects.filter(player=player, party=party, status='op').exists(),

        'party_characters': party_characters,
        'online_dict': online_dict,
        'players_count': party_characters.count(),

    })
