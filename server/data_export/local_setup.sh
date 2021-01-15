#!/bin/bash

#Activeate data export python virtual environment
source /export_venv/bin/activate

export DATA_EXPORT_DEV=1

#Create empty database
echo "Creating empty database"
python ../manage.py migrate

#Load fixtures
echo "Starting data load"
FILES=/server/data_export/U01DataFixtures/*.json
for f in $FILES
do
  echo "  ...loading data from $f" 
  #python ../manage.py loaddata $f
  python bulk_load.py $f 

done