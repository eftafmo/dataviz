#!/bin/bash

set -e;

# wait for web container to be up

until grep -q web /etc/hosts; do
  echo "Waiting for 'web' in /etc/hosts ..."
  sleep 1
done
echo "Found 'web' in /etc/hosts, proceeding"

echo "Running default entrypoint /scripts/entrypoint.sh ..."
exec nginx -g "daemon off;"
