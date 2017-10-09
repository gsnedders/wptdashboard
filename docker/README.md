```sh
docker build -t wptd .

docker run \
    -e "PLATFORM_ID=edge-15-windows-10-sauce" \
    -e "RUN_PATH=gamepad" \
    -e "SAUCE_KEY=rutabaga" \
    -e "SAUCE_USER=rutabaga" \
    -p 0.0.0.0:4445:4445 \
    wptd
```

Push a new version to the registry. Be advised this is dangerous since all builds use this container.


```sh
IMAGE_NAME=gcr.io/wptdashboard/wptd-testrun
docker tag wptd $IMAGE_NAME
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
