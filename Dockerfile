FROM python:3.9

RUN apt-get update && apt-get install -y cmake
ADD requirements.pip .
RUN pip install -r requirements.pip

ADD *.py .

CMD [ "python", "app.py" ]