FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends git gcc curl apt-utils libc-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/* 
# upgrade pip

# RUN python3 -m pip install --upgrade pip

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system --ignore-pipfile
RUN pip install importlib_metadata
RUN pip install celery
RUN pip install django-redis

# copy the whole app
COPY . /app

EXPOSE 8000
# CMD ["/bin/bash", "/app/entrypoint.sh"]