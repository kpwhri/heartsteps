FROM heartsteps_service-template:latest

RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh >/dev/null && \
    bash Anaconda3-5.0.1-Linux-x86_64.sh -b  >/dev/null && \
    rm Anaconda3-5.0.1-Linux-x86_64.sh && \
    ln -s /root/anaconda3/bin/conda /usr/local/bin/conda

RUN conda create -q -y -n py36 python=3.6.8 && \
    conda install -q -y --name py36 -c conda-forge pyreadr && \
    conda install -q -y --name py36  -c conda-forge pandas && \
    conda install -q -y --name py36 -c conda-forge jupyter && \
    conda install -q -y --name py36 -c conda-forge tensorflow && \
    conda install -q -y --name py36  -c conda-forge gpflow  && \
    conda install -q -y pytorch torchvision -c pytorch && \
	conda install -q -y --name py36 -c conda-forge scikit-learn && \
    conda clean --all

RUN /root/anaconda3/envs/py36/bin/pip install -q git+https://github.com/cornellius-gp/gpytorch.git && \
    /root/anaconda3/envs/py36/bin/pip install -q pandas

ADD . /pooling-service
WORKDIR /pooling-service

RUN chmod -R 777 ./
RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data
RUN chmod +x update.sh

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi --log-level debug
