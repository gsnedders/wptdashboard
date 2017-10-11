import json
import os
import subprocess
import time


def main():
    platform_id, platform = get_and_validate_platform()

    assert os.environ['SAUCE_KEY'], 'SAUCE_KEY env var required'
    assert os.environ['SAUCE_USER'], 'SAUCE_USER env var required'

    config = {
        'sauce_key': os.environ['SAUCE_KEY'],
        'sauce_user': os.environ['SAUCE_USER'],
        'sauce_tunnel_id': '%s_%s' % (platform_id, time.time()),
        'wpt_path': os.path.expanduser('~/web-platform-tests'),
        'local_report_filepath': os.path.expanduser('~/wptreport.log')
    }

    # Hack because Sauce expects a different name
    # Maybe just change it in browsers.json?
    if platform['browser_name'] == 'edge':
        sauce_browser_name = 'MicrosoftEdge'
    else:
        sauce_browser_name = platform['browser_name']
    product = 'sauce:%s:%s' % (sauce_browser_name, platform['browser_version'])

    patch_wpt(config, platform)

    command = [
        './wpt', 'run', product,
        '--sauce-platform=%s' % platform['os_name'],
        '--sauce-key=%s' % config['sauce_key'],
        '--sauce-user=%s' % config['sauce_user'],
        # There's a bug in wptrunner if you supply this
        # By default it will download SC, which is okay
        # '--sauce-connect-binary=%s' % config['sauce_connect_path'],
        '--sauce-tunnel-id=%s' % config['sauce_tunnel_id'],
        '--no-restart-on-unexpected',
        # '--processes=2',
        '--run-by-dir=3',
        '--no-manifest-update', # TODO JUST FOR DEBUGGING
        '--log-mach=-',
        '--log-wptreport=%s' % config['local_report_filepath'],
        '--install-fonts'
    ]
    if os.environ['RUN_PATH']:
        command.insert(3, os.environ['RUN_PATH'])

    subprocess.call(command, cwd=config['wpt_path'])

    with open(config['local_report_filepath']) as f:
        report = json.load(f)

    assert len(report['results']) > 0, (
        '0 test results, something went wrong, stopping.')

    summary = report_to_summary(report)
    print 'WOOOOOOOOOOOOOOOOOOOOOOO!!!!!'
    print summary # TODO remove this before removing path!


def patch_wpt(config, platform):
    """Applies util/wpt.patch to WPT.

    The patch is necessary to keep WPT running on long runs.
    jeffcarp has a PR out with this patch:
    https://github.com/w3c/web-platform-tests/pull/5774
    """
    with open(os.path.expanduser('~/wptdashboard/wpt.patch')) as f:
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
    return platform_id, browsers.get(platform_id)


def report_to_summary(wpt_report):
    test_files = {}

    for result in wpt_report['results']:
        test_file = result['test']
        assert test_file not in test_files, (
            'Assumption that each test_file only shows up once broken!')

        if result['status'] in ('OK', 'PASS'):
            test_files[test_file] = [1, 1]
        else:
            test_files[test_file] = [0, 1]

        for subtest in result['subtests']:
            if subtest['status'] == 'PASS':
                test_files[test_file][0] += 1

            test_files[test_file][1] += 1

    return test_files


if __name__ == '__main__':
    main()
