# Containerized builds

In order to improve deployability and test local reproducability, wpt.fyi runs its tests in a Docker container, `wptd-testrun`.

### Building the container

```sh
docker build -t wptd-testrun .
```

### Running the tests

```sh
PLATFORM_ID=edge-15-windows-10-sauce
SAUCE_USER=rutabaga
SAUCE_KEY=rutabaga
WPT_SHA=$(cd ~/gh/w3c/web-platform-tests && git rev-parse HEAD | head -c 10)
docker run \
    -e "PLATFORM_ID=$PLATFORM_ID" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "RUN_PATH=gamepad" \
    -e "WPT_SHA=$WPT_SHA" \
    -e "SAUCE_USER=$SAUCE_USER" \
    -e "SAUCE_KEY=$SAUCE_KEY" \
    -p 4445:4445 \
    wptd-testrun
```

Remove the `RUN_PATH` variable if you wish to run the whole suite.

Add the `PROD_RUN=True` if you want the run to upload its results and create a TestRun. You can also pass `PROD_WET_RUN=True` which will do exactly the same thing but create a TestRun that won't show up in the dashboard (for integration testing).

## Push a new version to the registry

Be advised this is dangerous as all builds use this container.

```sh
IMAGE_NAME=gcr.io/wptdashboard/wptd-testrun
docker tag wptd-testrun $IMAGE_NAME
gcloud docker -- push $IMAGE_NAME
```

## Start a test run VM

This starts a VM that runs a containerized test run and uploads the results.

The VM startup script will automatically pull Sauce credentials from the GCE metadata store. You can pass additional args as metadata.

```sh
PLATFORM_ID=edge-15-windows-10-sauce
VM_NAME=test-vm-docker-run
WPT_SHA=$(cd ~/gh/w3c/web-platform-tests && git rev-parse HEAD | head -c 10)
gcloud compute instances create $VM_NAME \
    --metadata-from-file startup-script=vm-startup.sh \
    --metadata PLATFORM_ID=$PLATFORM_ID,RUN_PATH=gamepad,WPT_SHA=$WPT_SHA \
    --zone us-central1-c \
    --scopes=compute-rw,storage-rw
```

To view the logs:

```sh
gcloud compute ssh $VM_NAME

# In the VM
tail -f /var/log/syslog
```
