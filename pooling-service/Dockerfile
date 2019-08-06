FROM heartsteps_service-template:latest

RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh && \
    bash Anaconda3-5.0.1-Linux-x86_64.sh -b && \
    rm Anaconda3-5.0.1-Linux-x86_64.sh && \
    ln -s /root/anaconda3/bin/conda /usr/local/bin/conda

RUN conda create -n py36 python=3.6 && \
    conda install --name py36 -c conda-forge pyreadr && \
    conda install --name py36 -c conda-forge jupyter && \
    conda install  --name py36 -c conda-forge tensorflow && \
    conda install --name py36  -c conda-forge gpflow  && \
    conda install pytorch torchvision -c pytorch && \
    pip install git+https://github.com/cornellius-gp/gpytorch.git

ADD . /pooling-service
WORKDIR /pooling-service

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi
