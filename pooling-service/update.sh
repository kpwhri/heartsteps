#!/bin/bash
for i in "$@"
do
case $i in
-u=*|--users=*)
USERS="${i#*=}"
shift # past argument=value
;;
esac
done
#echo $USERS
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python create_dirs.py
conda deactivate
sleep 2
Rscript merge.r
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python run.py $USERS
conda deactivate
sleep 2
Rscript merge.r
sleep 2
Rscript merge_time.r
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python run_time.py
sleep 2
Rscript merge_time.r
