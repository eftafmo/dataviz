# EEA Grants Dataviz installation

These instructions assume you're deploying to Azure Containers, and have already set up an account on the Azure portal.

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    ```shell
    az login --tenant fdf06eeb-4370-4758-bad3-26541c642925
    ```

1. Log into Azure
    ```shell
    docker login azure

    # for production, make sure you're using the correct tenant-id and subscription-id:
    #docker login azure --tenant-id fdf06eeb-4370-4758-bad3-26541c642925
    #az account set --subscription d0c8e6b7-00d8-49e3-bb85-7a0467fc4dcc
    ```

1. Set up shell variables and Docker context:
    ```shell
    # deploy to staging:
    source docker/set_context_staging.sh

    # deploy to production:
    #source docker/set_context_production.sh
    ```

1. Set up secrets

    1. If it's a first-time deployment, set up a Key Vault:

        ```shell
        az keyvault create --location $EEAG_REGION --name $EEAG_VAULT --resource-group $EEAG_RESOURCE_GROUP
        ```

       Then enter secrets:

        ```shell
        az keyvault secret set --vault-name $EEAG_VAULT --name secret-key --value 'not-so-secret'
        ```

       The following secrets are required:

       * `allowed-hosts`: Domain name for the site. _(Set `*` to allow cron scripts to do their job. Remote requests come in via the load balancer, therefore this doesn't open up a security hole.)_
       * `secret-key`: A random string for Django's `SECRET_KEY` setting.
       * `sentry-dsn`: Sentry DSN for the back-end.
       * `sentry-environment`: Sentry environment name.
       * `google-analytics-property-id`: Google Analytics tracking ID, e.g. `UA-12345-1`.
       * `fqdn`: Domain name for the site.
       * `certbot-email`: Email to use when requesting a certificate from Let's Encrypt. Used for [Expiration Emails](https://letsencrypt.org/docs/expiration-emails/).

    1. Download secrets and generate a configuration file:

        ```shell
        docker/azure-get-secrets.py $EEAG_VAULT web > docker/azure-web.env
        docker/azure-get-secrets.py $EEAG_VAULT nginx > docker/azure-nginx.env
        ```

1. Create volumes:
    ```shell
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-elasticsearchdata
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-webdb
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-weblogs
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-webroot
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-nginxconfig
    docker volume create --storage-account $EEAG_STORAGE_ACCOUNT we-p-fmo-dockervolume-upload
    ```

1. Upload nginx configuration:
    ```shell
    az storage copy -s docker/azure-nginx.conf -d "https://$EEAG_STORAGE_ACCOUNT.file.core.windows.net/we-p-fmo-dockervolume-nginxconfig/nginx.conf"
    az storage copy -s docker/azure-entrypoint.sh -d "https://$EEAG_STORAGE_ACCOUNT.file.core.windows.net/we-p-fmo-dockervolume-nginxconfig/entrypoint.sh"
    ```

1. Prepare the database file to work on Azure persistent volumes:
    ```shell
    sqlite3 eeag.sqlite3
    sqlite> PRAGMA journal_mode=wal;
    ```

1. Upload the database file:
    ```shell
    az storage copy -s eeag.sqlite3 -d "https://$EEAG_STORAGE_ACCOUNT.file.core.windows.net/we-p-fmo-dockervolume-webdb/eeag.sqlite3"
    ```

1. Deploy the app:
    ```shell
    docker compose -f docker-compose-azure.yml up
    ```

1. Rebuild indexes:
    ```shell
    docker exec -it we-p-fmo-docker-dataeeagrantsorg-cg_web bash  # log in to web container
    ./manage.py rebuild_index --noinput
    exit  # log out of web container
    ```
