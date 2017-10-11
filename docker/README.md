In order to improve debugging cycle time, there are two containers:

- `wptd-base` - includes all necessary files
- `wptd-testrun` - the final container for running the tests

First build the base container.

```sh
cd docker/wptd-base
docker build -t wptd-base .
```

Then you can build the test run container.

```sh
docker build -t wptd-testrun .

docker run \
    -e "PLATFORM_ID=edge-15-windows-10-sauce" \
    -e "RUN_PATH=gamepad" \
    -e "SAUCE_KEY=rutabaga" \
    -e "SAUCE_USER=rutabaga" \
    -p 4445:4445 \
    wptd-testrun
```

Push a new version to the registry. Be advised this is dangerous since all builds use this container.


```sh
IMAGE_NAME=gcr.io/wptdashboard/wptd-testrun
docker tag wptd-testrun $IMAGE_NAME
gcloud docker -- push $IMAGE_NAME
```

Start a VM that runs a containerized test run and uploads the results.

```sh
gcloud compute instances create test-vm-docker-run \
    --metadata-from-file startup-script=vm-startup.sh \
    --zone us-central1-c \
    --image-project cos-cloud \
    --image cos-stable-55-8872-76-0
```
