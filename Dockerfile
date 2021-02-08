FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y build-essential cmake python-dev python-setuptools libboost-python-dev libboost-thread-dev

ADD requirements.pip .
RUN pip install -r requirements.pip

ENV PYTHONUNBUFFERED True

ADD *.py ./
VOLUME [ "/tmp" ]

ENTRYPOINT gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 0 app:flask_app