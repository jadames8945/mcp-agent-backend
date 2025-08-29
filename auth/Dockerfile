FROM python:3.13-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/auth/.venv/bin:$PATH" \
    VIRTUAL_ENV="/auth/.venv"

WORKDIR /auth

RUN pip install poetry==1.8.2

COPY ./auth/pyproject.toml ./auth/poetry.lock* ./

RUN poetry install

COPY auth/ auth/
COPY common/ common/

EXPOSE 8946

RUN chmod +x auth/prestart.sh

CMD ["./auth/prestart.sh"]