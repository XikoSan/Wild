from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Вернуть страницу по подготовленному сету данных
def get_thing_page(queryset, page, count):
    # Создаем набор страниц с игроками, по 50 тушек на страницу
    paginator = Paginator(queryset, count)
    # вытаскиваем нкжную страницу
    try:
        lines = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        lines = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее  количество страниц, возвращаем последнюю.
        lines = paginator.page(paginator.num_pages)

    return lines
