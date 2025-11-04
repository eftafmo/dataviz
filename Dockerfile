FROM node:22 AS frontend-builder

ENV APP_HOME=/var/local/dataviz

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

ADD package.json package-lock.json postcss.config.js vite.config.mjs ./
RUN npm install

COPY assets/ assets/
COPY public/ public/

RUN NODE_ENV=production npm run build


FROM python:3.12-slim

# roles:
#   front - publishes ports to the world; this depends on run/docker-compose though...

LABEL maintainer="andrei.melis@eaudeweb.ro" \
      roles="front" \
      name="web"

ENV APP_HOME=/var/local/dataviz \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN mkdir -p $APP_HOME \
 && mkdir -p /var/local/logs \
 && touch ~/.bashrc

WORKDIR $APP_HOME

COPY requirements/ requirements/
RUN pip install -r requirements/base.txt -c requirements/constraints.txt

COPY pytest.ini pytest.ini
COPY .coveragerc .coveragerc
COPY dv/ dv/
COPY assets/ assets/
COPY templates/ templates/
COPY manage.py manage.py

COPY ./docker/localsettings.py dv/
COPY ./docker/entrypoint.sh ./docker/import.sh ./docker/wait_for_app.sh /bin/

COPY --from=frontend-builder /var/local/build /var/local/build
ENTRYPOINT ["entrypoint.sh"]
