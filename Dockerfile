FROM python:3.9
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx  libglib2.0-0
RUN pip install --upgrade pip

ADD requirements.pip .
RUN pip install -r requirements.pip

ENV PYTHONUNBUFFERED True

ADD *.py ./
VOLUME [ "/tmp" ]

RUN pip freeze
ENTRYPOINT python app.py