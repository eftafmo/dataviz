Data and results portal for EEA & Norway Grants - data.eeagrants.org
=========================================


[![Docker build](https://img.shields.io/docker/build/eftafmo/dataviz.svg)](https://hub.docker.com/r/eftafmo/dataviz/builds) [![Updates](https://pyup.io/repos/github/eftafmo/dataviz/shield.svg)](https://pyup.io/repos/github/eftafmo/dataviz/)



## Development installation guide

### Prerequisites

* Obtain access to [Eeag gitlab](https://gitlab.com/eftafmo/eeag.docker)
* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)


### Installing the application


1. Get the docker installation repository and the source code:

        $ git clone git@gitlab.com:eftafmo/eeag.docker.git
        $ cd eeag.docker
        $ git clone git@github.com:eftafmo/dataviz.git src

2. Prepare environment:

        $ cd eeag/
        $ cp docker-compose.override-dev.yml.example docker-compose.override.yml
        $ cp web/web.dev.env.example web/web.env
        $ cd ..


3. Replace database file with the latest version from production

        $ mkdir db
        $ scp edwsys@data.eeagrants.org:/var/local/eeag.docker/db/eeag.sqlite3  db/eeag.sqlite3

5. Create local settings:

        $ cd src
        $ cp dv/localsettings.py.example dv/localsettings.py
        $ cd ..

6. Start services:

        $ cd eeag/
        $ docker-compose up -d

6. Reload solr schema:

        $ ./solr/reload_schema.sh


7. Step in the container,install requirements and rebuild solr indexes.

        $ docker exec -it eeag_web bash
        $ pip install -r requirements.dev.txt
        $ python manage.py rebuild_index --noinput

8. Install npm and start webpack dev server(*leave this container open*):

        $ export NODE_ENV=debug
        $ npm install
        $ npm run dev

9. Open another web container and start the django server:

        $ docker exec -it eeag_web bash
        $ python manage.py runserver 0.0.0.0:8000
