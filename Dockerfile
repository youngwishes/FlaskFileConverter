FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y libpq-dev build-essential

RUN apt-get install ffmpeg libavcodec-extra --yes

WORKDIR /usr/src/

COPY requirements.txt /usr/src/

RUN pip install --upgrade pip && python -m pip install -r requirements.txt

COPY app /user/src/app

WORKDIR /user/src/app/

ENV SQLALCHEMY_DATABASE_URI="postgresql://flaskaudio:12345@localhost:5432/flaskaudio"

EXPOSE 5000
