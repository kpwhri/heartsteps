#!/usr/bin/env bash

cloud_sql_proxy -instances=$GCLOUD_DB_INSTANCE=tcp:5432 -credential_file=gce.json & ./manage.py migrate