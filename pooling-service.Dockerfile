FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base=3.3.3-1

# Install google cloud sdk and gcsfuse
ENV CLOUD_SDK_REPO cloud-sdk-jessie
ENV GCSFUSE_REPO gcsfuse-jessie
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y gcsfuse google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin

ADD service-template/utils /utils 
ENV PATH $PATH:/utils
RUN chmod +x /utils/*

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

ADD ./pooling-service /pooling-service
WORKDIR /pooling-service

RUN chmod -R 777 ./
RUN pip install -r requirements.txt
RUN Rscript install.r

ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/google-storage-service.json
ENV googleStorageBucket walking-suggestions-data
RUN chmod +x update.sh

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
    gcloud config set project heartsteps-kpwhri && \
    gcsfuse --implicit-dirs walking-suggestions-data ./data && \
    gunicorn -b 0.0.0.0:8080 wsgi --log-level debug
