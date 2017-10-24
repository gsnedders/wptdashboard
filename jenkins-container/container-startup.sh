#cd /web-platform-tests && git pull
#cd /wptdashboard && git pull
#cd /

source /web-platform-tests/tools/ci/lib.sh
hosts_fixup

python /run.py
