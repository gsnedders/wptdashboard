# This file should be as small as possible.
# Functionality should be in the container when possible.

METADATA=http://metadata.google.internal/computeMetadata/v1

# Log into Docker
SVC_ACCT=$METADATA/instance/service-accounts/default
ACCESS_TOKEN=$(curl -H 'Metadata-Flavor: Google' $SVC_ACCT/token | cut -d'"' -f 4)
docker login -u _token -p $ACCESS_TOKEN https://gcr.io

# These are expected to be passed in (RUN_PATH can be empty).
PLATFORM_ID=$(curl $METADATA/instance/attributes/PLATFORM_ID -H "Metadata-Flavor: Google")
RUN_PATH=$(curl $METADATA/instance/attributes/RUN_PATH -H "Metadata-Flavor: Google")
WPT_SHA=$(curl $METADATA/instance/attributes/WPT_SHA -H "Metadata-Flavor: Google")

# These are expected to be stored in the project's metadata.
SAUCE_USER=$(curl $METADATA/project/attributes/sauce_user -H "Metadata-Flavor: Google")
SAUCE_KEY=$(curl $METADATA/project/attributes/sauce_key -H "Metadata-Flavor: Google")
UPLOAD_SECRET=$(curl $METADATA/project/attributes/upload_secret -H "Metadata-Flavor: Google")

echo "PLATFORM_ID: $PLATFORM_ID"
echo "RUN_PATH: $RUN_PATH"

docker run --rm \
    -e "PLATFORM_ID=$PLATFORM_ID" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "RUN_PATH=$RUN_PATH" \
    -e "SAUCE_USER=$SAUCE_USER" \
    -e "SAUCE_KEY=$SAUCE_KEY" \
    -e "PROD_WET_RUN=True" \
    -e "UPLOAD_SECRET=$UPLOAD_SECRET" \
    -p 4445:4445 \
    --log-driver=gcplogs \
    gcr.io/wptdashboard/wptd-testrun

# Delete the VM after use.
## gcloud compute instances delete $(hostname) --quiet --zone=us-central1-c
