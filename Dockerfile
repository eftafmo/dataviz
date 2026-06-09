FROM node:24-slim AS frontend-builder

ENV APP_HOME=/var/local/dataviz

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

ADD package.json package-lock.json postcss.config.cjs vite.config.mjs ./
RUN npm install

COPY assets/ assets/
COPY public/ public/

RUN NODE_ENV=production npm run build


FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

ARG UV_ARGS=""

ENV APP_HOME=/var/local/dataviz
ENV UV_SYSTEM_PYTHON=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# roles:
#   front - publishes ports to the world; this depends on run/docker-compose though...

LABEL maintainer="andrei.melis@eaudeweb.ro" \
      roles="front" \
      name="web"

RUN mkdir -p $APP_HOME \
 && mkdir -p /var/local/logs \
 && touch ~/.bashrc

WORKDIR $APP_HOME

ADD pyproject.toml .
ADD uv.lock .
RUN uv sync --locked --no-default-groups $UV_ARGS

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
