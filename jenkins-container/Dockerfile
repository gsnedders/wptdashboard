FROM jenkinsci/jnlp-slave

USER root

RUN apt-get update

# wpt run dependencies
RUN apt-get install -y python-pip
RUN pip install virtualenv

RUN apt-get install -y git

# Needed for hosts_fixup
RUN apt-get install -y sudo

# Used for running FF and Chrome
RUN apt-get install -y xvfb

# Used for running FF
RUN apt-get install -y \
    libnss3-tools \
    libgtk-3-common \
    libdbus-glib-1-2

# Install Google Cloud SDK for uploading results with gsutil and
# terminating the instance.
RUN curl -sSL https://sdk.cloud.google.com | bash
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

# Pre-clone repos and pre-generate manifest.
# Test runs will still need to pull and update
# but this speeds up startup.
RUN git clone https://github.com/w3c/wptdashboard.git
# RUN git clone https://github.com/w3c/web-platform-tests.git
# RUN /web-platform-tests/wpt manifest

RUN pip install 'requests==2.13.0'

# Expose Sauce Connect port
EXPOSE 4445

ADD . /

RUN mkdir /build
