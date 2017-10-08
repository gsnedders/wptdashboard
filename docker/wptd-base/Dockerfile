FROM python:2.7

ADD . /

RUN apt-get update
RUN apt-get install -y git

RUN git clone https://github.com/w3c/wptdashboard.git
RUN git clone https://github.com/w3c/web-platform-tests.git
