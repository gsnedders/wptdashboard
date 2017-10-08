import json
import os
import subprocess


def main():
    add_hosts()
    platform = get_and_validate_platform()

    assert os.environ['SAUCE_KEY'], 'SAUCE_KEY env var required'
    assert os.environ['SAUCE_USER'], 'SAUCE_USER env var required'

    config = {
        'sauce_key': os.environ['SAUCE_KEY'],
        'sauce_user': os.environ['SAUCE_USER'],
        'sauce_connect_path': '/sc-4.4.9-linux/bin/sc',
        'sauce_tunnel_id': 'rutabaga', # TODO change
        'wpt_path': '/web-platform-tests',
    }

    # Hack because Sauce expects a different name
    # Maybe just change it in browsers.json?
    if platform['browser_name'] == 'edge':
        sauce_browser_name = 'MicrosoftEdge'
    else:
        sauce_browser_name = platform['browser_name']

    product = 'sauce:%s:%s' % (sauce_browser_name, platform['browser_version'])

    patch_wpt(config, platform)

    path = 'cookies' # TODO parameterize this
    run_command('./wpt', 'run', product, path,
        '--sauce-platform=%s' % platform['os_name'],
        '--sauce-key=%s' % config['sauce_key'],
        '--sauce-user=%s' % config['sauce_user'],
        '--sauce-connect-binary=%s' % config['sauce_connect_path'],
        # '--sauce-tunnel-id=%s' % config['sauce_tunnel_id'],
        '--no-restart-on-unexpected',
        # '--processes=2',
        '--run-by-dir=3',
        '--no-manifest-update', # TODO JUST FOR DEBUGGING
        cwd='/web-platform-tests'
    )


def add_hosts():
    hosts = [
        '127.0.0.1 web-platform.test',
        '127.0.0.1 www.web-platform.test',
        '127.0.0.1 www1.web-platform.test',
        '127.0.0.1 www2.web-platform.test',
        '127.0.0.1 xn--n8j6ds53lwwkrqhv28a.web-platform.test',
        '127.0.0.1 xn--lve-6lad.web-platform.test',
        '0.0.0.0 nonexistent-origin.web-platform.test',
    ]
    with open('/etc/hosts', 'w') as f:
        for host in hosts:
            f.write('%s\n' % host)


def run_command(*args, **kwargs):
    return_code = subprocess.check_call(args, cwd=kwargs.get('cwd', '/'))
    assert return_code == 0, (
        'Got non-0 return code: '
        '%d from command %s' % (return_code, command))


def patch_wpt(config, platform):
    """Applies util/wpt.patch to WPT.

    The patch is necessary to keep WPT running on long runs.
    jeffcarp has a PR out with this patch:
    https://github.com/w3c/web-platform-tests/pull/5774
    """
    with open('/wpt.patch') as f:
        patch = f.read()

    # The --sauce-platform command line arg doesn't
    # accept spaces, but Sauce requires them in the platform name.
    # https://github.com/w3c/web-platform-tests/issues/6852
    patch = patch.replace('__platform_hack__', '%s %s' % (
        platform['os_name'], platform['os_version'])
    )

    p = subprocess.Popen(
        ['git', 'apply', '-'], cwd=config['wpt_path'], stdin=subprocess.PIPE
    )
    p.communicate(input=patch)


def get_and_validate_platform():
    with open('browsers.json') as f:
        browsers = json.load(f)

    platform_id = os.environ['PLATFORM_ID']
    assert platform_id, 'PLATFORM_ID env var required'
    assert platform_id in browsers, 'PLATFORM_ID not found in browsers.json'
    return browsers.get(platform_id)


if __name__ == '__main__':
    main()
