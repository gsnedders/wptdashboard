# This replaces run/run.py
import json
import gzip
import os
import requests
import subprocess
import time
import re


def main():
    # TODO somehow after --install browser verify browser
    # version or change platform ID to correct browser version
    # This can be done by running `wpt install firefox` and then verifying

    # TODO report OS version when creating TestRun

    # TODO record WPT revision inside test run

    args = {
        'prod_run': bool(os.environ.get('PROD_RUN', False)),
        'prod_wet_run': bool(os.environ.get('PROD_WET_RUN', False)),
        'SHA': os.environ.get('WPT_SHA'),
        'upload_secret': os.environ.get('UPLOAD_SECRET'),
        'sauce_key': os.environ.get('SAUCE_KEY', ''),
        'sauce_user': os.environ.get('SAUCE_USER', ''),
        'jenkins_job_name': os.environ.get('JOB_NAME'),
        'wpt_path': os.environ.get('WPT_PATH'),
        'build_path': os.environ.get('BUILD_PATH'),
        'run_path': os.environ.get('RUN_PATH', ''),
    }

    # Arg validation
    assert args['wpt_path'], '`WPT_PATH` env var required.'
    assert not args['wpt_path'].endswith('/'), '`WPT_PATH` cannot end with /.'
    assert args['build_path'], '`BUILD_PATH` env var required.'
    assert not args['build_path'].endswith('/'), '`BUILD_PATH` cannot end with /.'
    if args['prod_run'] or args['prod_wet_run']:
        assert args['upload_secret'], 'must pass UPLOAD_SECRET for prod run.'

    platform_id, platform = get_and_validate_platform(args['build_path'])

    GSUTIL_BINARY = '/root/google-cloud-sdk/bin/gsutil'
    PROD_HOST = 'https://wptdashboard.appspot.com'
    GS_RESULTS_BUCKET = 'wptd'
    BUILD_PATH = '/build'
    LOCAL_LOG_FILEPATH = '/wptd-testrun.log'
    LOCAL_REPORT_FILEPATH = "%s/wptd-%s-%s-report.log" % (
        BUILD_PATH, args['SHA'], platform_id
    )
    SUMMARY_PATH = '%s/%s-summary.json.gz' % (args['SHA'], platform_id)
    LOCAL_SUMMARY_GZ_FILEPATH = "%s/%s" % (BUILD_PATH, SUMMARY_PATH)
    GS_RESULTS_FILEPATH_BASE = "%s/%s/%s" % (
        BUILD_PATH, args['SHA'], platform_id
    )
    GS_HTTP_RESULTS_URL = 'https://storage.googleapis.com/%s/%s' % (
        GS_RESULTS_BUCKET, SUMMARY_PATH
    )

    SUMMARY_FILENAME = '%s-%s-summary.json.gz' % (args['SHA'], platform_id)
    SUMMARY_HTTP_URL = 'https://storage.googleapis.com/%s/%s' % (
        GS_RESULTS_BUCKET, SUMMARY_FILENAME
    )

    if platform.get('sauce'):
        assert args['sauce_key'], 'SAUCE_KEY env var required'
        assert args['sauce_user'], 'SAUCE_USER env var required'
        SAUCE_TUNNEL_ID = '%s_%s' % (platform_id, int(time.time()))

    assert len(args['SHA']) == 10, 'SHA must a WPT SHA[:10]'

    # Hack because Sauce expects a different name
    # Maybe just change it in browsers.json?
    if platform['browser_name'] == 'edge':
        sauce_browser_name = 'MicrosoftEdge'
    else:
        sauce_browser_name = platform['browser_name']
    product = 'sauce:%s:%s' % (sauce_browser_name, platform['browser_version'])

    patch_wpt(args['build_path'], args['wpt_path'], platform)

    if platform.get('sauce'):
        command = [
            './wpt', 'run', product,
            '--sauce-platform=%s' % platform['os_name'],
            '--sauce-key=%s' % args['sauce_key'],
            '--sauce-user=%s' % args['sauce_user'],
            '--sauce-tunnel-id=%s' % SAUCE_TUNNEL_ID,
            '--no-restart-on-unexpected',
            '--processes=2',
            '--run-by-dir=3',
            '--log-mach=-',
            '--log-wptreport=%s' % LOCAL_REPORT_FILEPATH,
            '--install-fonts'
        ]
        if args['run_path']:
            command.insert(3, args['run_path'])
    else:
        command = [
            'xvfb-run', '--auto-servernum',
            './wpt', 'run',
            platform['browser_name'],
            '--install-fonts',
            '--install-browser',
            '--yes',
            '--log-mach=%s' % LOCAL_LOG_FILEPATH,
            '--log-wptreport=%s' % LOCAL_REPORT_FILEPATH,
        ]
        if args['run_path']:
            command.insert(5, args['run_path'])

    if args['jenkins_job_name']:
        # Expects a job name like chunk_2_of_4
        chunks = re.findall(r'(\d+)_of_(\d+)', args['jenkins_job_name'])
        chunk_num, total_chunks = chunks[0]
        command.extend([
            '--this-chunk=%s' % chunk_num,
            '--total-chunks=%s' % total_chunks,
        ])

    return_code = subprocess.call(command, cwd=args['wpt_path'])

    print('==================================================')
    print('Finished WPT run')
    print('Return code from wptrunner: %s' % return_code)

    with open(LOCAL_REPORT_FILEPATH) as f:
        report = json.load(f)

    assert len(report['results']) > 0, (
        '0 test results, something went wrong, stopping.')

    summary = report_to_summary(report)

    print('==================================================')
    print('Writing summary.json.gz to local filesystem')
    write_gzip_json(LOCAL_SUMMARY_GZ_FILEPATH, summary)
    print('Wrote file %s' % LOCAL_SUMMARY_GZ_FILEPATH)

    print('==================================================')
    print('Writing individual result files to local filesystem')
    for result in report['results']:
        test_file = result['test']
        filepath = '%s%s' % (GS_RESULTS_FILEPATH_BASE, test_file)
        write_gzip_json(filepath, result)
        print('Wrote file %s' % filepath)

    if not (args['prod_run'] or args['prod_wet_run']):
        print('==================================================')
        print('Stopping here (pass PROD_RUN env var to upload results).')
        return

    print('==================================================')
    print('Uploading results to gs://%s' % GS_RESULTS_BUCKET)

    # TODO: change this from rsync to cp
    command = [GSUTIL_BINARY, '-m', '-h', 'Content-Encoding:gzip',
               'rsync', '-r', args['SHA'], 'gs://wptd/%s' % args['SHA']]
    return_code = subprocess.check_call(command, cwd=args['build_path'])
    assert return_code == 0
    print('Successfully uploaded!')
    print('HTTP summary URL: %s' % GS_HTTP_RESULTS_URL)

    print('==================================================')
    print('Creating new TestRun in the dashboard...')
    url = '%s/test-runs' % PROD_HOST

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
            'browser_name': final_browser_name,
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


def patch_wpt(build_path, wpt_path, platform):
    """Applies util/wpt.patch to WPT.

    The patch is necessary to keep WPT running on long runs.
    jeffcarp has a PR out with this patch:
    https://github.com/w3c/web-platform-tests/pull/5774
    """
    with open('%s/wpt.patch' % build_path) as f:
        patch = f.read()

    # The --sauce-platform command line arg doesn't
    # accept spaces, but Sauce requires them in the platform name.
    # https://github.com/w3c/web-platform-tests/issues/6852
    patch = patch.replace('__platform_hack__', '%s %s' % (
        platform['os_name'], platform['os_version'])
    )

    p = subprocess.Popen(
        ['git', 'apply', '-'], cwd=wpt_path, stdin=subprocess.PIPE
    )
    p.communicate(input=patch)


def get_and_validate_platform(build_path):
    with open('%s/browsers.json' % build_path) as f:
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
