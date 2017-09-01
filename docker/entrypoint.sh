#!/usr/bin/env bash

init() {
    ./manage.py migrate
    ./manage.py collectstatic --noinput
}

wait_solr() {
    while ! nc -z solr 8983; do
        echo "Waiting for Solr server solr:8983 ..."
        sleep 1
    done

}

install_crontab() {
    echo "Installing crontab"
    #printenv | sed 's/^\(.*\)$/export \1/g' | grep -E "(EDW|MYSQL|EEAG)" &> ~/.bashrc
    crontab /etc/crontab.dataviz
}

/usr/sbin/cron
install_crontab

if [ -z "$1" ]; then
  init &&
  wait_solr &&
  exec gunicorn dv.wsgi:application \
         --name eeag \
         --bind 0.0.0.0:8000 \
         --workers $NUM_WORKERS \
         --access-logfile - \
         --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec "$@"
fi