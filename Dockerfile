FROM python:3.9-slim-buster

ADD requirements.pip .
RUN pip install -r requirements.pip

ENV PYTHONUNBUFFERED True

ADD *.py ./
VOLUME [ "/tmp" ]

ENTRYPOINT python app.py