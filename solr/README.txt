# Deploy on debian

$ apt-get install default-jre

$ apt-get install solr-jetty
OR
$ wget http://mirrors.m247.ro/apache/lucene/solr/5.5.4/solr-5.5.4.tgz
$ tar -xzf solr-5.5.4.tgz
$ cd solr-5.5.4
$ ./bin/install_solr_service.sh

- create core or copy one in solr dir (eg: /var/solr/data)
- copy solr/schema.xml from this repo into the core conf/ dir

$ service solr restart


