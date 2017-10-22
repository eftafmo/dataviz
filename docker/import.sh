#!/bin/bash

UPLOAD_DIR=/var/local/upload
date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py import $UPLOAD_DIR
date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py import_news
DONE_DIR=`date '+%Y%m%d'`
mkdir $UPLOAD_DIR/$DONE_DIR
mv $UPLOAD_DIR/*.xlsx $UPLOAD_DIR/$DONE_DIR
date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py rebuild_index --noinput
date '+%Y-%m-%d %H:%M:%S'
