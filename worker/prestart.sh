#! /usr/bin/env bash

source /worker/.venv/bin/activate
celery -A worker.tasks worker --loglevel=info --concurrency=4
