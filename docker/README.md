

```sh
docker build -t wptd .

docker run \
    -e "PLATFORM_ID=edge-15-windows-10-sauce" \
    -e "SAUCE_KEY=rutabaga" \
    -e "SAUCE_USER=rutabaga" \
    -p 0.0.0.0:4445:4445 \
    wptd
```
