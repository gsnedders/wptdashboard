# using wptd-base for debugging, probably don't
# need it once we're good
FROM wptd-base

ADD . /

# Expose Sauce Connect port
EXPOSE 4445

CMD ["python", "/run.py"]
