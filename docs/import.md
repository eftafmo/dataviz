# Importing data

Instructions on recreating the database with data imported from all periods.

---

Requirements:

 - application must be installed/deployed
 - must have credentials to the SQL Server for 2014-2021 and set in the environment variables
   (see [docker/localsettings.py](../docker/localsettings.py)).:
   - `MSSQL_SERVER`
   - `MSSQL_USERNAME`
   - `MSSQL_PASSWORD`
   - `MSSQL_DATABASE`
 - must run the import on a server that is allowed by the firewall on the SQL Server
   (e.g. testing server, production server, via VPN) for the 2014-2021 period
 - must have a folder with xlsx files for the 2009-2014 period
 - must have a json file for period for the 2004-2009 period


### Starting from a fresh database

1. Run migrations
    ```shell
    python manage.py migrate
    ```

2. Load fixtures
    ```shell
    python manage.py load_fixtures initial
    ```

3. Run import script. This will import data for all periods (`2004-2009`, `2009-2014`, `2014-2021`).
    ```shell
    python manage.py import --directory=./2009-2014 --json-path=./allocation_2004-2009.json --noinput
    ```

4. Import news
    ```shell
    python manage.py import_news
    ```

5. Rebuild indexes
    ```shell
    python manage.py rebuild_index --noinput
    ```

### Updating data for a specific period

A temporary DB can be used to update the DB for a period without downtime. See also [import.sh](../docker/import.sh)
for an example usage.

1. Copy existing DB to a temporary location
    ```shell
    cp /var/local/db/eeag.sqlite3 /tmp/eeag.sqlite3
    ```

2. Run the import script for the specific period that needs updating (arguments specific to other periods can
   be omitted):
    ```shell
    # for 2004-2009
    env DJANGO_DB_PATH=/tmp/eeag.sqlite3 python manage.py import --json-path=./allocation_2004-2009.json --period=2004-2009

    # for 2009-2014
    env DJANGO_DB_PATH=/tmp/eeag.sqlite3 python manage.py import --directory=./2009-2014 --period=2009-2014

    # for 2014-2021
    env DJANGO_DB_PATH=/tmp/eeag.sqlite3 python manage.py import --period=2014-2021
    ```

3. Move the DB back from the tmp location:
    ```shell
    mv /tmp/eeag.sqlite3 /var/local/db/eeag.sqlite3
    ```

4. Rebuild indexes. *This cannot be done in a tmp location at this time, so searches will be unavailable
   while this runs:*
    ```shell
    python manage.py rebuild_index --noinput
    ```

5. _(Optional)_ Clear caches:
    ```shell
    rm -rf /var/tmp/django_cache
    ```
