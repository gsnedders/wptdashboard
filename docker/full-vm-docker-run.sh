export PLATFORM_ID=edge-15-windows-10-sauce
export RUN_PATH=gamepad

export META_ROOT=http://metadata.google.internal/computeMetadata/v1/project/attributes
export SAUCE_KEY=$(curl $META_ROOT/sauce_key -H "Metadata-Flavor: Google")
export SAUCE_USER=$(curl $META_ROOT/sauce_user -H "Metadata-Flavor: Google")

source web-platform-tests/tools/ci/lib.sh

hosts_fixup

cd wptdashboard
git checkout docker
python docker/run.py
