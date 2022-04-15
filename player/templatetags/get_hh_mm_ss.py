from django import template

register = template.Library()


@register.filter(name='get_hh_mm_ss')
def get_hh_mm_ss(obj):
    hours, remainder = divmod(obj, 3600)
    minutes, seconds = divmod(remainder, 60)

    str = '{}:{}:{}'.format(hours, minutes, seconds)

    return str
    # return str(datetime.timedelta(seconds=obj))
