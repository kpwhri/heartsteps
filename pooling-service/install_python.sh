
wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
bash Anaconda3-5.0.1-Linux-x86_64.sh -b
rm Anaconda3-5.0.1-Linux-x86_64.sh

sudo ln -s /root/anaconda3/bin/conda /usr/local/bin/conda

conda create -n py36 python=3.6

conda install --name py36 -c conda-forge pyreadr
conda install --name py36 -c conda-forge jupyter

conda install  --name py36 -c conda-forge tensorflow
conda install --name py36  -c conda-forge gpflow 
conda install pytorch torchvision -c pytorch

pip install git+https://github.com/cornellius-gp/gpytorch.git
