FROM python:alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev python3-dev jpeg-dev zlib-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

CMD sh -c "python manage.py migrate --no-input && daphne -b 0.0.0.0 -p 80 wild_politics.asgi:application"