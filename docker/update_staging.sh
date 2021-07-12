#!/usr/bin/env bash

set -ev

cp "docker/docker-compose.override-staging.yml.example" "docker-compose.override.yml"
docker-compose build --pull
docker-compose up -d --remove-orphans
