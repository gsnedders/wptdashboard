IMAGE_NAME=wptd-testrun-jenkins

# Build the image
docker build -t $IMAGE_NAME .

# Run a small directory in FF and Edge (Sauce)
docker run \
  -p 4445:4445 \
  --entrypoint "/usr/bin/bash" $IMAGE_NAME \
  /wptdashboard/util/ci_container_inner.sh
