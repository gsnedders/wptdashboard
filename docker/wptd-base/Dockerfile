FROM python:2.7

RUN apt-get update

# sudo is needed for hosts_fixup
RUN apt-get install -y git sudo

# Pre-clone repos and pre-generate manifest.
# Test runs will still need to pull and update
# but this speeds up startup.
RUN git clone https://github.com/w3c/wptdashboard.git
RUN git clone https://github.com/w3c/web-platform-tests.git
RUN /web-platform-tests/wpt manifest
