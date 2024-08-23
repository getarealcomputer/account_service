FROM python:3.12

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

WORKDIR /project/account_service

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY .env pyproject.toml poetry.lock /project/account_service

RUN poetry install --no-root --no-dev

COPY . /project/account_service/

WORKDIR /project/account_service/account_service

EXPOSE 8000
