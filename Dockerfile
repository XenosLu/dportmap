FROM python:3.11.1-alpine3.17
# https://hub.docker.com/_/python
LABEL maintainer="xenos <xenos.lu@gmail.com>"

COPY . /dportmap

RUN apk add --no-cache \
            tzdata \
            &&\
    apk add --no-cache \
            docker-cli \
            curl \
            vim \
            tree \
            nethogs \
            miniupnpc \
            &&\
    rm -rf /root/.cache

RUN pip3 install --no-cache-dir -r /dportmap/requirements.txt
CMD ["python", "/dportmap/dportmap.py"]
