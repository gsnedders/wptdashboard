#FROM jenkinsci/jnlp-slave
FROM gcr.io/cloud-solutions-images/jenkins-k8s-slave

USER root

# Expose Sauce Connect port
EXPOSE 4445

RUN apt-get update

# wpt run dependencies
RUN apt-get install -y python-pip
RUN pip install virtualenv
RUN pip install 'requests==2.13.0'

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

RUN mkdir /build
ADD . /build
ADD ./MANIFEST.json /build/MANIFEST.json
RUN chown -R jenkins:jenkins /build

#RUN git clone https://github.com/w3c/wptdashboard.git /home/jenkins/wptdashboard
