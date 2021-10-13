# Importing data 

Instructions on recreating the database with data imported from all periods. 

---

Requirements:

 - application must be installed/deployed 
 - must have a folder with xlsx files for 2009-2014
 - must have a json file for period 2004-2009


### Starting from a fresh database

1. Run migrations
    ```shell
    python manage.py migrate
    ```

2. Load fixtures
    ```shell
    python manage.py load_initial_fixtures
    ```
   
3. Run import script
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
    env DJANGO_DB_PATH=/tmp/eeag.sqlite3 python manage.py import --directory=./2009-2014 --period=2009-2014 
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
