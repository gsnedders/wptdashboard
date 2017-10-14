# Containerized builds

In order to improve deployability and test local reproducability, wpt.fyi runs its tests in a Docker container, `wptd-testrun`.

### Building the container

```sh
docker build -t wptd-testrun .
```

### Running the tests locally

You can run the tests without building the container yourself by using the production version at `gcr.io/wptdashboard/wptd-testrun`.

Run the tests on Sauce:

```sh
PLATFORM_ID=edge-15-windows-10-sauce
SAUCE_USER=rutabaga
SAUCE_KEY=rutabaga
WPT_SHA=$(cd ~/gh/w3c/web-platform-tests && git rev-parse HEAD | head -c 10)
RUN_PATH=battery-status
docker run \
    -e "PLATFORM_ID=$PLATFORM_ID" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "RUN_PATH=$RUN_PATH" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "SAUCE_USER=$SAUCE_USER" \
    -e "SAUCE_KEY=$SAUCE_KEY" \
    -p 4445:4445 \
    wptd-testrun
```

Remove the `RUN_PATH` variable if you wish to run the whole suite.

Add the `PROD_RUN=True` if you want the run to upload its results and create a TestRun. You can also pass `PROD_WET_RUN=True` which will do exactly the same thing but create a TestRun that won't show up in the dashboard (for integration testing).

Run the tests on a local browser:

```sh
PLATFORM_ID=firefox-57.0-linux
WPT_SHA=$(cd ~/gh/w3c/web-platform-tests && git rev-parse HEAD | head -c 10)
RUN_PATH=battery-status
docker run \
    -e "PLATFORM_ID=$PLATFORM_ID" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "RUN_PATH=$RUN_PATH" \
    -e "WPT_SHA=$WPT_SHA" \
    wptd-testrun
```

## Push a new version to the registry

Be advised this is dangerous as all builds use this container.

```sh
docker build -t wptd-testrun .
IMAGE_NAME=gcr.io/wptdashboard/wptd-testrun
docker tag wptd-testrun $IMAGE_NAME
gcloud docker -- push $IMAGE_NAME
```

## Start a test run VM

This starts a VM that runs a containerized test run and uploads the results.

The VM startup script will automatically pull Sauce credentials from the GCE metadata store. You can pass additional args as metadata.

```sh
gcloud compute instances create $VM_NAME \
    --metadata-from-file startup-script=vm-startup.sh \
    --metadata PLATFORM_ID=$PLATFORM_ID,RUN_PATH=battery-status,WPT_SHA=$WPT_SHA \
    --zone us-central1-c \
    --scopes=compute-rw,storage-rw,cloud-platform \
    --image-project cos-cloud \
    --image cos-stable-55-8872-76-0
```

## Debugging

Watch the logs here:

```
VM_NAME=firefox-nightly-vm-1507940182
open https://console.cloud.google.com/logs/viewer?project=wptdashboard&organizationId=433637338589&minLogLevel=0&expandAll=false&interval=NO_LIMIT&resource=global&logName=projects%2Fwptdashboard%2Flogs%2Fgcplogs-docker-driver&filters=jsonPayload.instance.name:$VM_NAME
```

To tail the logs (for startup script debugging):

```sh
gcloud compute ssh $VM_NAME
sudo journalctl -f
```

Get a shell on the container:

```sh
docker run -it gcr.io/wptdashboard/wptd-testrun /bin/bash
```

Get a shell on a running container:

```sh
docker ps
docker exec -it $PROCESS_ID /bin/bash
```
