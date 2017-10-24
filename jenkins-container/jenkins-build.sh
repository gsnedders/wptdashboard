source /root/workspace/web-platform-tests/tools/ci/lib.sh
hosts_fixup
./wpt manifest
xvfb-run ./wpt run firefox battery-status --install-browser --yes
