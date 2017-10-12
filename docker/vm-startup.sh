# This file should be as small as possible.
# Functionality should be in the container when possible.

METADATA=http://metadata.google.internal/computeMetadata/v1

# These are expected to be passed in (RUN_PATH can be empty).
PLATFORM_ID=$(curl $METADATA/instance/attributes/PLATFORM_ID -H "Metadata-Flavor: Google")
RUN_PATH=$(curl $METADATA/instance/attributes/RUN_PATH -H "Metadata-Flavor: Google")

# These are expected to be stored in the project's metadata.
SAUCE_USER=$(curl $METADATA/project/attributes/sauce_user -H "Metadata-Flavor: Google")
SAUCE_KEY=$(curl $METADATA/project/attributes/sauce_key -H "Metadata-Flavor: Google")

# Install docker
apt-get install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common

curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | apt-key add -

add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install -y docker-ce

echo "PLATFORM_ID: $PLATFORM_ID"
echo "RUN_PATH: $RUN_PATH"

docker run --rm \
    -e "PLATFORM_ID=$PLATFORM_ID" \
    -e "RUN_PATH=$RUN_PATH" \
    -e "SAUCE_USER=$SAUCE_USER" \
    -e "SAUCE_KEY=$SAUCE_KEY" \
    -p 4445:4445 \
    gcr.io/wptdashboard/wptd-testrun
# This doesn't work on debian by default
#    --log-driver=gcplogs \

# Delete the VM after use.
gcloud compute instances delete $(hostname) --quiet --zone=us-central1-c
