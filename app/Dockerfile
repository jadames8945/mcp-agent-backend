FROM python:3.13-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/backend/.venv/bin:$PATH" \
    VIRTUAL_ENV="/backend/.venv"

WORKDIR /backend

RUN pip install poetry==1.8.2

COPY ./app/pyproject.toml ./app/poetry.lock* ./

RUN poetry install

COPY app/ app/
COPY worker/ worker/
COPY common/ common/
COPY auth/ auth/

EXPOSE 9889

RUN chmod +x app/prestart.sh

CMD ["./app/prestart.sh"]