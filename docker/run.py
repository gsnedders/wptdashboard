# This replaces run/run.py
import json
import gzip
import os
import subprocess
import time
import requests # Need to install


def main():
    platform_id, platform = get_and_validate_platform()

    args = {
        'prod_run': bool(os.environ.get('PROD_RUN', False)),
        'prod_wet_run': bool(os.environ.get('PROD_WET_RUN', False)),
        'SHA': os.environ.get('WPT_SHA'),
        'upload_secret': os.environ.get('UPLOAD_SECRET'),
        # TODO add sauce_* to args
    }

    config = {
        'wpt_path': '/web-platform-tests',
        'local_report_filepath': '/wptreport.log',
        'local_summary_gz_filepath': '/summary.json.gz',
        'gs_results_filepath_base': '/results',
        'gs_results_bucket': 'wptd',
        'gsutil_binary': '/root/google-cloud-sdk/bin/gsutil',
    }

    BUILD_PATH = '/build'
    LOCAL_REPORT_FILEPATH = "%s/wptd-%s-%s-report.log" % (
        BUILD_PATH, args['SHA'], platform_id
    )
    SUMMARY_PATH = '%s/%s-summary.json.gz' % (args['SHA'], platform_id)
    LOCAL_SUMMARY_GZ_FILEPATH = "%s/%s" % (BUILD_PATH, SUMMARY_PATH)
    GS_RESULTS_FILEPATH_BASE = "%s/%s/%s" % (
        BUILD_PATH, args['SHA'], platform_id
    )
    GS_HTTP_RESULTS_URL = 'https://storage.googleapis.com/%s/%s' % (
        config['gs_results_bucket'], SUMMARY_PATH
    )

    if args['prod_run'] or args['prod_wet_run']:
      assert args['upload_secret'], 'UPLOAD_SECRET must be passed for a prod run.'

    SUMMARY_FILENAME = '%s-%s-summary.json.gz' % (args['SHA'], platform_id)
    SUMMARY_HTTP_URL = 'https://storage.googleapis.com/%s/%s' % (
        config['gs_results_bucket'], SUMMARY_FILENAME
    )

    if platform.get('sauce'):
        assert os.environ['SAUCE_KEY'], 'SAUCE_KEY env var required'
        assert os.environ['SAUCE_USER'], 'SAUCE_USER env var required'
        config['sauce_key'] = os.environ['SAUCE_KEY']
        config['sauce_user'] = os.environ['SAUCE_USER']
        config['sauce_tunnel_id'] = '%s_%s' % (platform_id, int(time.time()))

    assert len(args['SHA']) == 10, 'SHA must be the first 10 digits of the WPT SHA'

    # Hack because Sauce expects a different name
    # Maybe just change it in browsers.json?
    if platform['browser_name'] == 'edge':
        sauce_browser_name = 'MicrosoftEdge'
    else:
        sauce_browser_name = platform['browser_name']
    product = 'sauce:%s:%s' % (sauce_browser_name, platform['browser_version'])

    # TODO check out args['SHA']!
    patch_wpt(config, platform)

    if platform.get('sauce'):
        command = [
            './wpt', 'run', product,
            '--sauce-platform=%s' % platform['os_name'],
            '--sauce-key=%s' % config['sauce_key'],
            '--sauce-user=%s' % config['sauce_user'],
            '--sauce-tunnel-id=%s' % config['sauce_tunnel_id'],
            '--no-restart-on-unexpected',
            '--processes=2',
            '--run-by-dir=3',
            '--log-mach=-',
            '--log-wptreport=%s' % config['local_report_filepath'],
            '--install-fonts'
        ]
        if os.environ['RUN_PATH']:
            command.insert(3, os.environ['RUN_PATH'])
    else:
        command = [
            'xvfb-run', '--auto-servernum',
            './wpt', 'run',
            'firefox',
            '--yes',
            '--processes=2',
            '--log-mach=-',
            '--log-wptreport=%s' % config['local_report_filepath'],
            '--install-fonts',
            '--install-browser'
        ]
        if os.environ['RUN_PATH']:
            command.insert(5, os.environ['RUN_PATH'])

    return_code = subprocess.call(command, cwd=config['wpt_path'])

    print('==================================================')
    print('Finished WPT run')
    print('Return code from wptrunner: %s' % return_code)

    with open(config['local_report_filepath']) as f:
        report = json.load(f)

    assert len(report['results']) > 0, (
        '0 test results, something went wrong, stopping.')

    summary = report_to_summary(report)

    print('==================================================')
    print('Writing summary.json.gz to local filesystem')
    write_gzip_json(config['local_summary_gz_filepath'], summary)
    print('Wrote file %s' % config['local_summary_gz_filepath'])

    print('==================================================')
    print('Writing individual result files to local filesystem')
    for result in report['results']:
        test_file = result['test']
        filepath = '%s%s' % (config['gs_results_filepath_base'], test_file)
        write_gzip_json(filepath, result)
        print('Wrote file %s' % filepath)

    if not (args['prod_run'] or args['prod_wet_run']):
        print('==================================================')
        print('Stopping here (pass PROD_RUN env var to upload results to WPTD).')
        return

    print('==================================================')
    print('Uploading results to gs://%s' % config['gs_results_bucket'])

    # TODO: change this from rsync to cp
    command = [config['gsutil_binary'], '-m', '-h', 'Content-Encoding:gzip',
               'rsync', '-r', args['SHA'], 'gs://wptd/%s' % args['SHA']]
    return_code = subprocess.check_call(command, cwd=BUILD_PATH)
    assert return_code == 0
    print('Successfully uploaded!')
    print('HTTP summary URL: %s' % GS_HTTP_RESULTS_URL)

    print('==================================================')
    print('Creating new TestRun in the dashboard...')
    url = '%s/test-runs' % config['wptd_prod_host']

    if args['prod_run']:
        final_browser_name = platform['browser_name']
    else:
        # The PROD_WET_RUN is identical to PROD_RUN, however the
        # browser name it creates will be prefixed by eval-,
        # causing it to not show up in the dashboard.
        final_browser_name = 'eval-%s' % platform['browser_name']

    response = requests.post(url, params={
            'secret': args['upload_secret']
        },
        data=json.dumps({
            'browser_name': platform['browser_name'],
            'browser_version': platform['browser_version'],
            'os_name': platform['os_name'],
            'os_version': platform['os_version'],
            'revision': args['SHA'],
            'results_url': GS_HTTP_RESULTS_URL
        }
    ))
    if response.status_code == 201:
        print('Run created!')
    else:
        print('There was an issue creating the TestRun.')

    print('Response status code:', response.status_code)
    print('Response text:', response.text)


def patch_wpt(config, platform):
    """Applies util/wpt.patch to WPT.

    The patch is necessary to keep WPT running on long runs.
    jeffcarp has a PR out with this patch:
    https://github.com/w3c/web-platform-tests/pull/5774
    """
    with open('/wptdashboard/util/wpt.patch') as f:
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
    with open('/wptdashboard/browsers.json') as f:
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


def write_gzip_json(filepath, payload):
    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError:
        pass

    with gzip.open(filepath, 'wb') as f:
        payload_str = json.dumps(payload)
        f.write(payload_str)

if __name__ == '__main__':
    main()
