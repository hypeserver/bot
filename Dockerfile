FROM python:3.9
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx  libglib2.0-0

# PIP & Poetry
RUN pip install --upgrade pip
COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.1.4
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

ENV PYTHONUNBUFFERED True

ADD *.py ./
ADD utils/ ./utils
VOLUME [ "/tmp" ]

RUN pip freeze

ENTRYPOINT gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 0 app:flask_app
