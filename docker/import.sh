#!/bin/bash

date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py import_news
$PYTHONPATH/python /var/local/dataviz/manage.py update_index dv.news --remove

UPLOAD_DIR=/var/local/upload
date '+%Y-%m-%d %H:%M:%S'
output=$($PYTHONPATH/python /var/local/dataviz/manage.py import $UPLOAD_DIR 2>&1)
if [ $? -eq 0 ]; then
	DONE_DIR=`date '+%Y%m%d'`
	mkdir $UPLOAD_DIR/$DONE_DIR
	mv $UPLOAD_DIR/*.xlsx $UPLOAD_DIR/$DONE_DIR
	date '+%Y-%m-%d %H:%M:%S'
	$PYTHONPATH/python /var/local/dataviz/manage.py rebuild_index --noinput
	date '+%Y-%m-%d %H:%M:%S'
else
	sentry-cli send-event -m "Import error: $output"
fi

