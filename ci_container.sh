IMAGE_NAME=wptd-testrun-jenkins

if [ -z "${SAUCE_USER}" ]; then
  echo "SAUCE_USER env var required."
  exit
fi
if [ -z "${SAUCE_KEY}" ]; then
  echo "SAUCE_KEY env var required."
  exit
fi

# Build the image
docker build -t $IMAGE_NAME .

# Run a small directory in FF and Edge (Sauce)
docker run \
  -p 4445:4445 \
  -e "SAUCE_USER=$SAUCE_USER" \
  -e "SAUCE_KEY=$SAUCE_KEY" \
  --entrypoint "/bin/bash" $IMAGE_NAME \
  /wptdashboard/util/ci_container_inner.sh
