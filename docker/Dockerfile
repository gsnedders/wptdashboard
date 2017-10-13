FROM python:2.7

RUN apt-get update

RUN apt-get install -y git
# sudo is needed for hosts_fixup
RUN apt-get install -y sudo
# xvfb is used for running FF and Chrome
RUN apt-get install -y xvfb

# Install Google Cloud SDK
# For uploading results with gsutil and terminating the instance.
RUN curl -sSL https://sdk.cloud.google.com | bash

# Pre-clone repos and pre-generate manifest.
# Test runs will still need to pull and update
# but this speeds up startup.
RUN git clone https://github.com/w3c/wptdashboard.git
RUN git clone https://github.com/w3c/web-platform-tests.git
RUN /web-platform-tests/wpt manifest

RUN pip install 'requests==2.13.0'

# Expose Sauce Connect port
EXPOSE 4445

ADD . /

RUN mkdir /build

CMD ["/bin/bash", "/container-startup.sh"]
