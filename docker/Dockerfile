FROM osgeo/gdal:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
    libspatialindex-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

#RUN pip3 install git+https://github.com/goatsweater/nrn-rnn.git
# During development just install some dependencies. Code will have to be mounted in.
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
# pip3 install -e .

#ENTRYPOINT [ "nrn" ]
#CMD [ "--help" ]