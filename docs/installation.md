# Server deployment using Docker

## Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

## Initial setup

```shell
mkdir -p /var/local/eeag/docker
cd /var/local/eeag

curl -o docker-compose.yml https://raw.githubusercontent.com/eftafmo/dataviz/master/docker-compose.yml
# Use docker-compose.override-prod.yml.example when deploying on prod
curl -o docker-compose.override.yml https://raw.githubusercontent.com/eftafmo/dataviz/master/docker/docker-compose.override-staging.yml.example

# Use web.prod.env.example when deploying on prod
curl -o docker/web.env https://raw.githubusercontent.com/eftafmo/dataviz/master/docker/web.staging.env.example
# edit secrets
vim docker/web.env

# update docker image version
vim docker-compose.override.yml

# start containers
docker-compose up -d

# copy data file
scp dataviz@data.eeagrants.org:eeag.sqlite3 /tmp/eeag.sqlite3
docker cp /tmp/eeag.sqlite3 eeag_web:/var/local/db/eeag.sqlite3

# clear cache and restart
docker exec eeag_web rm -rf /var/tmp/django_cache/
docker-compose restart web

# rebuild ES indexes
docker-compose exec web bash
python manage.py rebuild_index --noinput
exit

# Setup cron
# 0 0 * * * /bin/docker system prune -f >> /var/log/dataviz/docker-prune.log 2>&1
# 0 4 * * * /bin/docker exec eeag_web import.sh >> /var/log/dataviz/import.log 2>&1
crontab -e

# Setup nginx
curl -o /etc/nginx/conf.d/eeagrants.edw.ro.conf https://raw.githubusercontent.com/eftafmo/dataviz/master/docker/nginx.conf.staging.example

```
