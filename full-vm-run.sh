sudo apt-get update
sudo apt-get install -y git python-pip

sudo pip install virtualenv

git clone https://github.com/w3c/web-platform-tests.git
git clone https://github.com/w3c/wptdashboard.git

export PLATFORM_ID=edge-15-windows-10-sauce
export RUN_PATH=gamepad
export SAUCE_KEY=asdf
export SAUCE_USER=jeffcarp

source web-platform-tests/tools/ci/lib.sh

hosts_fixup

cd wptdashboard
git checkout docker
python docker/run.py
