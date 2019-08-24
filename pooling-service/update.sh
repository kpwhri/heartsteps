#!/bin/bash

sleep 2
for i in "$@"
do
case $i in
    -u=*|--users=*)
    USERS="${i#*=}"
    shift # past argument=value
    ;;
esac
done
echo $USERS
pwd
source activate py36
which python
python run.py $USERS
