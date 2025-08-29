# `python-base` sets up all our shared environment variables
FROM python:3.13-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/worker/.venv/bin:$PATH" \
    VIRTUAL_ENV="/worker/.venv"

WORKDIR /worker

RUN pip install poetry==1.8.2

COPY ./worker/pyproject.toml ./worker/poetry.lock* ./

RUN poetry install

COPY worker/ worker/
COPY app/ app/
COPY common/ common/

RUN chmod +x worker/prestart.sh

CMD ["./worker/prestart.sh"]

