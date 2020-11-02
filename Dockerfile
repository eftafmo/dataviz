FROM python:3.6-slim-buster AS frontend

ENV APP_HOME=/var/local/dataviz

RUN runDeps="curl gnupg" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && curl -sL https://deb.nodesource.com/setup_8.x | bash - \
 && echo 'Package: *' > /etc/apt/preferences.d/nodesource \
 && echo 'Pin: origin deb.nodesource.com' >> /etc/apt/preferences.d/nodesource \
 && echo 'Pin-Priority: 600' >> /etc/apt/preferences.d/nodesource \
 && apt-get install -y nodejs \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p $APP_HOME

WORKDIR $APP_HOME
ADD package.json package-lock.json postcss.config.js ./
RUN npm install
ADD . $APP_HOME
RUN NODE_ENV=production npm run build


FROM python:3.6-slim-buster

# roles:
#   front - publishes ports to the world; this depends on run/docker-compose though...
#   cron - runs cron daemon
LABEL maintainer="andrei.melis@eaudeweb.ro" \
      roles="front,cron" \
      name="web"

#RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list

ENV APP_HOME=/var/local/dataviz \
    PYTHONUNBUFFERED=1

RUN runDeps="git curl cron" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && curl -sL https://sentry.io/get-cli/ | bash \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p $APP_HOME \
 && mkdir -p /var/local/logs \
 && touch ~/.bashrc

WORKDIR $APP_HOME
COPY ./docker/crontab /etc/crontab.dataviz
COPY ./docker/entrypoint.sh ./docker/import.sh /bin/
ADD requirements.txt ./docker/requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements-docker.txt
ADD . $APP_HOME
COPY ./docker/localsettings.py $APP_HOME/dv/
COPY --from=frontend /var/local/build /var/local/build
ENTRYPOINT ["entrypoint.sh"]
