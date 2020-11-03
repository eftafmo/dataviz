#!/bin/sh
docker exec -it eeag_web python manage.py build_solr_schema --filename /var/local/dataviz/schema.xml
docker exec -it eeag_web python manage.py patch_schema /var/local/dataviz/schema.xml
docker cp eeag_web:/var/local/dataviz/schema.xml ./schema.xml
docker cp ./schema.xml eeag_solr:/solr_home/eeagrants/conf/
docker run --rm --name solr_schemafixer --volumes-from eeag_solr alpine rm /solr_home/eeagrants/conf/managed-schema
curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=eeagrants"
