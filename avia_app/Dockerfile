FROM python:3.7-slim
LABEL maintainer="nest1304@mail.ru"
RUN apt-get update
RUN mkdir /avia_app

COPY requirements.txt /avia_app
WORKDIR /avia_app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /avia_app
EXPOSE 8080
# CMD [ "python3", "app.py" ]