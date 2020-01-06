ARG DEBIAN_NAME=stretch
FROM wanderijames/pyenv:debian

RUN pip3.6 install django==3.0 celery