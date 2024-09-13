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

CMD sh -c "python manage.py migrate --no-input && python manage.py collectstatic --no-input && uvicorn wild_politics.asgi:application --host 0.0.0.0 --port 80 --workers 4"
