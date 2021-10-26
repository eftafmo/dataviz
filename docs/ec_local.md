# Run EC local on Docker

### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)


### Install EC on Docker


1. Create a new docker-compose.yml using the following lines

    ```shell
    version: '2'
    services:
      elasticsearch:
        image: elasticsearch:7.14.1
        container_name: eeag_elasticsearch
        environment:
          - discovery.type=single-node
          - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
        volumes:
          - elasticsearch_data:/usr/share/elasticsearch/data
        ports:
          - 9200:9200
        networks:
          - elastic
        restart: "always"

    volumes:
      elasticsearch_data:

    networks:
      elastic:
   ```

2. Install and start EC service:
   ```shell
   docker-compuse up -d
   ```
3. Check if you get a response when hit [localhost:9200](http://localhost:9200):, if you get a response, that means EC is running.

4. Install the requirements or check if you have the latest version of django-haystack
    ```shell
    pip install -r requirements.dev.txt
    ```
    OR
    ```shell
    pip install django-haystack -U
    ```
5. Replace [HAYSTACK_CONNECTIONS](https://github.com/eftafmo/dataviz/blob/data-model/dv/localsettings.py.example#:~:text=%7D-,HAYSTACK_CONNECTIONS%20%3D%20%7B,%7D,-%23%20TODO%20use%20env) settings in [localsettings.py](https://github.com/eftafmo/dataviz/blob/data-model/dv/localsettings.py.example):
    ```python
    HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
        "URL": "http://localhost:9200/",
        "INDEX_NAME": "eeagrants",
        "BATCH_SIZE": 999,
        "SILENTLY_FAIL": False,
        },
    }
    ```
6. Rebuild index using the following command
    ```shell
    ./manage.py rebuild_index
    ```