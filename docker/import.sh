#!/bin/bash

date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py import /var/local/upload
date '+%Y-%m-%d %H:%M:%S'
$PYTHONPATH/python /var/local/dataviz/manage.py import_news
