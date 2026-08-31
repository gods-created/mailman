#!/bin/sh

touch db.sqlite
alembic upgrade head

exec python -m gunicorn main:app \
    --bind 0.0.0.0:8001 \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 60