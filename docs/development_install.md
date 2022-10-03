# Developer documentation

## Local installation guide using Docker

### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installing the application

1. Get the docker installation repository and the source code:

        git clone git@github.com:eftafmo/dataviz.git
        cd dataviz

1. Prepare environment:

        cp docker/docker-compose.override-dev.yml.example docker-compose.override.yml
        cp docker/web.dev.env.example docker/web.env

1. Create local settings:

        cp dv/localsettings.py.example dv/localsettings.py

1. Start services:

        docker-compose up -d

1. Replace database file with the latest version from production

        scp dataviz@data.eeagrants.org:eeag.sqlite3 /tmp/eeag.sqlite3
        docker cp /tmp/eeag.sqlite3 eeag_web:/var/local/db/eeag.sqlite3

1. Step in the container, install requirements and rebuild indexes.

        docker-compose exec web bash
        pip install -r requirements.dev.txt
        python manage.py rebuild_index --noinput

1. Install npm and start webpack dev server(*leave this container open*):

        npm install
        npm run dev

1. Open another web container and start the django server:

        docker-compose exec web bash
        python manage.py runserver 0.0.0.0:8000

## Local installation without Docker

```shell
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.dev.txt
nvm use 16
npm install
cp dv/localsettings.py.example dv/localsettings.py

# Copy data file from prod/test
mkdir -p ../db
scp dataviz@data.eeagrants.org:eeag.sqlite3 ../db

# See es_local.md if you also need Elasticsearch

# start Django and frontend server
python manage.py runserver 0:8000
# in a new terminal
npm run dev
```
