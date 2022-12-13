FROM python:3.11.1-alpine3.16
# https://hub.docker.com/_/python
LABEL maintainer="xenos <xenos.lu@gmail.com>"
ENV PS1 '\h:\w\$ '

COPY . /dportmap

RUN apk add --no-cache \
            tzdata \
            &&\
            ln -snf /usr/share/zoneinfo/$TZ /etc/localtime &&\
            echo $TZ > /etc/timezone &&\
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
