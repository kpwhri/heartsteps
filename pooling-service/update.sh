#!/bin/bash

sleep 2
python create_dirs.py
Rscript merge.r
for i in "$@"
do
case $i in
    -u=*|--users=*)
    USERS="${i#*=}"
    shift # past argument=value
    ;;
esac
done
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python run.py $USERS
Rscript merge.r
