FROM python:2.7

ADD . /

RUN apt-get update
RUN apt-get install -y git

RUN git clone https://github.com/w3c/wptdashboard.git
RUN git clone https://github.com/w3c/web-platform-tests.git

RUN curl -O https://saucelabs.com/downloads/sc-4.4.9-linux.tar.gz \
    && gunzip sc-4.4.9-linux.tar.gz \
    && tar -xvf sc-4.4.9-linux.tar

RUN /web-platform-tests/wpt manifest
