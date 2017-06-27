# Deploy on debian

$ apt-get install default-jre

$ apt-get install solr-jetty
OR
$ wget http://mirrors.m247.ro/apache/lucene/solr/5.5.4/solr-5.5.4.tgz
$ tar -xzf solr-5.5.4.tgz
$ cd solr-5.5.4
$ ./bin/install_solr_service.sh

- create core (default name: eeagrants) or copy one in solr dir (eg: /var/solr/data). TODO: which configset to copy?
- copy solr/schema.xml from this repo into the core conf/ dir
- TODO: patch solrconfig.xml

$ service solr restart

# re-Index data

$ ./manage.py rebuild_index

# re-create schema.xml

$ ./manage.py build_solr_schema

