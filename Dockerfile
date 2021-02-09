FROM python:3.9-slim-buster
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev

ADD requirements.pip .
RUN pip install -r requirements.pip

ENV PYTHONUNBUFFERED True

ADD *.py ./
VOLUME [ "/tmp" ]

ENTRYPOINT python app.py