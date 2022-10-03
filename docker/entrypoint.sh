#!/usr/bin/env bash

init() {
    ./manage.py migrate
    ./manage.py collectstatic --noinput
}

wait_elasticsearch() {
    while ! nc -z elasticsearch 9200; do
        echo "Waiting for ES server elasticsearch:9200 ..."
        sleep 1
    done

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