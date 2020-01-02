#!/bin/bash
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python create_dirs_time.py
conda deactivate
sleep 2
Rscript merge_time.r
conda init bash > /dev/null
source ~/.bashrc
conda activate py36
python run_time.py
conda deactivate
sleep 2
Rscript merge_time.r
