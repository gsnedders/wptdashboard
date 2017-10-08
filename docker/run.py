import os
import subprocess


def main():
    add_hosts()
    run_command('/web-platform-tests/wpt', 'run', 'sauce:edge:15')


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


def run_command(*args):
    return_code = subprocess.check_call(args, cwd='/')
    assert return_code == 0, (
        'Got non-0 return code: '
        '%d from command %s' % (return_code, command))


if __name__ == '__main__':
    main()
