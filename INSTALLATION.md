# EEA Grants Dataviz installation

These instructions assume you're deploying to Azure Containers, and have already set up an account on the Azure portal.

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

1. Set up an Azure context in Docker:
    ```shell
    docker login azure
    docker context create aci eeagstaging
    source docker/set_context.sh eeagstaging
    ```

1. Set up secrets

    1. If it's a first-time deployment, set up a Key Vault:

        ```shell
        az keyvault create --location northeurope --name eeagsecrets --resource-group eeagstaging
        ```

       Then enter secrets:

        ```shell
        az keyvault secret set --vault-name eeagsecrets --name secret-key --value 'not-so-secret'
        ```

       The following secrets are required:

       * `allowed-hosts`: Domain name for the site.
       * `secret-key`: A random string for Django's `SECRET_KEY` setting.
       * `sentry-dsn`: Sentry DSN for the back-end.
       * `sentry-environment`: Sentry environment name.
       * `google-analytics-property-id`: Google Analytics tracking ID, e.g. `UA-12345-1`.
       * `fqdn`: Domain name for the site.
       * `certbot-email`: Email to use when requesting a certificate from Let's Encrypt. Used for [Expiration Emails](https://letsencrypt.org/docs/expiration-emails/).

    1. Download secrets and generate a configuration file:

        ```shell
        docker/azure-get-secrets.py eeagsecrets web > docker/azure-web.env
        docker/azure-get-secrets.py eeagsecrets nginx > docker/azure-nginx.env
        ```

1. Create volumes:
    ```shell
    docker volume create --storage-account eeagstorage solrhome
    docker volume create --storage-account eeagstorage solrlogs
    docker volume create --storage-account eeagstorage webdb
    docker volume create --storage-account eeagstorage weblogs
    docker volume create --storage-account eeagstorage webroot
    docker volume create --storage-account eeagstorage nginxconfig
    docker volume create --storage-account eeagstorage upload
    ```

1. Upload nginx configuration:
    ```shell
    az storage copy -s docker/azure-nginx.conf -d 'https://eeagstorage.file.core.windows.net/nginxconfig/nginx.conf'
    az storage copy -s docker/azure-entrypoint.sh -d 'https://eeagstorage.file.core.windows.net/nginxconfig/entrypoint.sh'
    ```

1. Prepare the database file to work on Azure persistent volumes:
    ```shell
    sqlite3 eeag.sqlite3
    sqlite> PRAGMA journal_mode=wal;
    ```

1. Upload the database file:
    ```shell
    az storage copy -s eeag.sqlite3 -d 'https://eeagstorage.file.core.windows.net/webdb/eeag.sqlite3'
    ```

1. Deploy the app:
    ```shell
    docker compose -f docker-compose-azure.yml up
    ```

1. Reload Solr schema:
    ```shell
    docker exec -it dataviz_web bash  # log in to web container
    ./manage.py build_solr_schema --filename /var/local/db/schema.xml
    ./manage.py patch_schema /var/local/db/schema.xml
    exit  # log out of web container

    az storage copy -s 'https://eeagstorage.file.core.windows.net/webdb/schema.xml' -d 'https://eeagstorage.file.core.windows.net/solrhome/eeagrants/conf/schema.xml'

    docker exec -it dataviz_solr bash  # log in to solr container
    rm /solr_home/eeagrants/conf/managed-schema
    curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=eeagrants"
    exit  # log out of solr container
    ```

1. Rebuild indexes:
    ```shell
    docker exec -it dataviz_web bash  # log in to web container
    ./manage.py rebuild_index --noinput
    exit  # log out of web container
    ```
