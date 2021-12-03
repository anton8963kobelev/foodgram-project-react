FROM python:3.7.9

WORKDIR /app

COPY . .

RUN python3 -m pip install --upgrade pip && pip install -r ./requirements.txt

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000