# `python-base` sets up all our shared environment variables
FROM python:3.13-slim AS python-base

# Set enviorment variables for Python and Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

# set working directory
WORKDIR /app

#Install poetry
RUN pip install poetry==1.8.2

# Copy the pyproject.toml file and the poetry.lock
COPY ./mcp_server/pyproject.toml ./mcp_server/poetry.lock* ./

#Install dependencies using poetry
RUN poetry install

#Expose port for the application
EXPOSE 9000

#Copy the mcp_server directory to app
COPY mcp_server/  mcp_server/
COPY common/ common/

#Ensure prestart as executable permissions
RUN chmod +x mcp_server/prestart.sh

#Set command to run prestart script
CMD [ "./mcp_server/prestart.sh" ]
