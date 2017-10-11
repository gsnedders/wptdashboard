METADATA=http://metadata.google.internal/computeMetadata/v1
SVC_ACCT=$METADATA/instance/service-accounts/default
ACCESS_TOKEN=$(curl -H 'Metadata-Flavor: Google' $SVC_ACCT/token | cut -d'"' -f 4)
docker login -u _token -p $ACCESS_TOKEN https://gcr.io

SAUCE_USER=$(curl $METADATA/project/attributes/sauce_user -H "Metadata-Flavor: Google")
SAUCE_KEY=$(curl $METADATA/project/attributes/sauce_key -H "Metadata-Flavor: Google")

docker run --rm \
    -e "PLATFORM_ID=edge-15-windows-10-sauce" \
    -e "RUN_PATH=fetch" \
    -e "SAUCE_USER=$SAUCE_USER" \
    -e "SAUCE_KEY=$SAUCE_KEY" \
    -p 4445:4445 \
    --log-driver=gcplogs \
    gcr.io/wptdashboard/wptd-testrun
