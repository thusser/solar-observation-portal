FROM python:3.7-slim

EXPOSE 80
WORKDIR /observation-portal
CMD gunicorn observation_portal.wsgi --bind=0.0.0.0:8080 --worker-class=gevent --workers=4 --timeout=300

COPY . /observation-portal

RUN apt-get update \
  && apt-get install -y gfortran
#  && pip install 'numpy>=1.16,<1.17'

RUN pip install django-ocs-observation-portal

RUN mkdir static && python manage.py collectstatic --noinput
