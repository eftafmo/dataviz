#!/usr/bin/env bash

set -e

wait-for-it --timeout 60 --service localhost:8000
