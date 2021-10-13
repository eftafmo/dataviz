#!/usr/bin/env bash

set -ev
date "+%Y-%m-%d %H:%M:%S"

manage="/var/local/dataviz/manage.py"
tmp_db="/tmp/temp.eeag.sqlite3"

app_db="$DJANGO_DB_PATH"
if [ -z "$app_db" ]
then
  app_db="/var/local/db/eeag.sqlite3"
fi

# Clean up tmp path, in case there were some failed runs
rm -f "$tmp_db" || true

# Copy the current db as starting point
cp "$app_db" "$tmp_db"

# Import new data in the temporary db
env DJANGO_DB_PATH="$tmp_db" python "$manage" import --period="2014-2021" --noinput
env DJANGO_DB_PATH="$tmp_db" python "$manage" import_news

# Replace the live db
mv "$tmp_db" "$app_db"

# Rebuild indexes from the live db
python "$manage" rebuild_index --noinput
