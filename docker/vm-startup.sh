METADATA=http://metadata.google.internal/computeMetadata/v1
SVC_ACCT=$METADATA/instance/service-accounts/default
ACCESS_TOKEN=$(curl -H 'Metadata-Flavor: Google' $SVC_ACCT/token | cut -d'"' -f 4)
docker login -u _token -p $ACCESS_TOKEN https://gcr.io

docker run --rm \
    -e "PLATFORM_ID=edge-15-windows-10-sauce" \
    -e "RUN_PATH=gamepad" \
    -e "SAUCE_KEY={REPLACE ME}" \
    -e "SAUCE_USER={REPLACE ME}" \
    --log-driver=gcplogs \
    gcr.io/wptdashboard/wptd-testrun
