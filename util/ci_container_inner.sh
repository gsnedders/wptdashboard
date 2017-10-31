export WPT_PATH=/web-platform-tests

git clone --depth 1 https://github.com/w3c/web-platform-tests $WPT_PATH

source $WPT_PATH/tools/ci/lib.sh
hosts_fixup

export BUILD_PATH=/wptdashboard
export RUN_PATH=battery-status
export WPT_SHA=$(cd $WPT_PATH && git rev-parse HEAD | head -c 10)

export PLATFORM_ID=firefox-57.0-linux
python /wptdashboard/run/jenkins.py

export PLATFORM_ID=edge-15-windows-10-sauce
export SAUCE_USER=$SAUCE_USER
export SAUCE_KEY=$SAUCE_KEY
python /wptdashboard/run/jenkins.py
