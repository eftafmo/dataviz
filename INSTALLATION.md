# EEA Grants Dataviz installation

These instructions assume you're deploying to Azure Containers, and have already set up an account on the Azure portal.

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

1. Set up an Azure context in Docker:
    ```shell
    docker login azure
    docker context create aci eeagstaging
    source docker/set_context.sh eeagstaging
    ```

1. Create volumes:
    ```shell
    (set +x; for name in solrhome solrlogs webdb weblogs webroot nginxconfig; do docker volume create --storage-account eeagstorage $name; done)
    ```

1. Deploy the app:
    ```shell
    docker compose -f docker-compose-azure.yml up
    ```

1. Upload nginx configuration and reload nginx:
    ```shell
    az storage copy -s docker/nginx.conf -d 'https://eeagstorage.file.core.windows.net/nginxconfig/nginx.conf'
    docker exec -it dataviz_nginx sh  # log in to nginx container
    kill -HUP 1  # reload nginx configuration
    ```
