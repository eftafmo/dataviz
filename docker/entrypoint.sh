#!/usr/bin/env bash

init() {
    ./manage.py migrate
    ./manage.py collectstatic --noinput
}

wait_elasticsearch() {
  wait-for-it --timeout 60 --service "elasticsearch:9200"
}

if [ -z "$1" ]; then
  init &&
  wait_elasticsearch &&
  exec gunicorn dv.wsgi:application \
         --name eeag \
         --bind 0.0.0.0:8000 \
         --workers $NUM_WORKERS \
         --timeout 300 \
         --access-logfile - \
         --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec "$@"
fi
