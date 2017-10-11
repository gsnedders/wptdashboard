FROM wptd-base

ADD . /

#RUN apt-get update
#RUN apt-get install -y git

# RUN /bin/bash -c "source /web-platform-tests/tools/ci/lib.sh; hosts_fixup"

# Pre-clone repos and pre-generate manifest.
# Test runs will still need to pull and update
# but this speeds up startup.
#RUN git clone https://github.com/w3c/wptdashboard.git
#RUN git clone https://github.com/w3c/web-platform-tests.git
#RUN /web-platform-tests/wpt manifest

# Expose Sauce Connect port
EXPOSE 4445

# CMD ["python", "/run.py"]
CMD ["/bin/bash", "/run.sh"]
