from django import template

from player.player_settings import PlayerSettings

register = template.Library()


@register.inclusion_tag('war/redesign/template_svg/war_icon.html')
def war_icon(player, icon_class, classes, style = ''):

    #  Настройки цветов профиля
    setts = None

    main_color = '28353E'
    sub_color = '284E64'
    text_color = 'FFFFFF'
    button_color = 'EB9929'

    if PlayerSettings.objects.filter(player=player).exists():
        setts = PlayerSettings.objects.get(player=player)

        main_color = setts.color_back
        sub_color = setts.color_block
        text_color = setts.color_text
        button_color = setts.color_acct



    return {
        # требуемая иконка
        'icon_class': icon_class,
        # цвета
        'main_color': main_color,
        'sub_color': sub_color,
        'text_color': text_color,
        'button_color': button_color,

        'classes': classes,
        'style': style,
    }
