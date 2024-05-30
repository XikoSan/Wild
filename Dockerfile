FROM mirror.gcr.io/library/python:3.8-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev python3-dev jpeg-dev zlib-dev\
    icu-dev \
    gettext \
    gettext-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime

COPY . .

CMD sh -c "python manage.py migrate --no-input && python manage.py collectstatic --no-input && daphne -b 0.0.0.0 -p 80 wild_politics.asgi:application"