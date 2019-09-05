#!/bin/bash

sleep 2
python create_dirs.py
for i in "$@"
do
case $i in
    -u=*|--users=*)
    USERS="${i#*=}"
    shift # past argument=value
    ;;
esac
done
source activate py36
python run.py $USERS
