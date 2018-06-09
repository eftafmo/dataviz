FROM python:3.6-slim

ENV PYTHONUNBUFFERED=1

# roles:
#   front - publishes ports to the world; this depends on run/docker-compose though...
#   cron - runs cron daemon
LABEL maintainer="andrei.melis@eaudeweb.ro" \
      roles="front,cron" \
      name="web"

#RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list

ENV APP_HOME=/var/local/dataviz \
    PATH=/var/local/scripts:$PATH \
    NODE_ENV=production

RUN runDeps="vim git curl cron netcat-traditional gnupg" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && apt-get clean \
 && rm -vrf /var/lib/apt/lists/* \
 && curl -sL https://deb.nodesource.com/setup_8.x | bash - \
 && apt-get install -y nodejs \
 && curl -sL https://sentry.io/get-cli/ | bash \
 && mkdir -p $APP_HOME \
 && mkdir -p /var/local/logs \
 && touch ~/.bashrc

COPY ./docker/crontab /etc/crontab.dataviz
COPY ./docker/entrypoint.sh ./docker/import.sh /bin/

ADD requirements.txt \
    ./docker/requirements-docker.txt \
    package.json postcss.config.js \
    $APP_HOME/

WORKDIR $APP_HOME

RUN npm install \
 && pip install -r requirements-docker.txt

ADD . $APP_HOME
COPY ./docker/localsettings.py $APP_HOME/dv/
RUN NODE_ENV=production npm run build

ENTRYPOINT ["entrypoint.sh"]
