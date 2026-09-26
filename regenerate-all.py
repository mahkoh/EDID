#!/usr/bin/env python3
#
# Regenerates all reports.
#
# Usage: ./regenerate-all.py <edid-decode> [jobs]    (default jobs: number of CPUs)

import os
import re
import subprocess
import sys
from multiprocessing import Pool

HEX = re.compile(rb'^(?:[a-f0-9]{32}|[a-f0-9 ]{47})$', re.M)
SERIAL = re.compile(rb'Serial Number: .*')
NAME = re.compile(r'[A-F0-9]{12}')

edid_decode = None


def init(path):
    global edid_decode
    edid_decode = path


def regenerate(path):
    with open(path, 'rb') as f:
        data = f.read()
    hexdata = b''.join(m.group(0) + b'\n' for m in HEX.finditer(data))
    out = subprocess.run([edid_decode, '-c', '--skip-sha'], input=hexdata,
                         stdout=subprocess.PIPE).stdout
    out = SERIAL.sub(b'Serial Number: ...', out)
    with open(path, 'wb') as f:
        f.write(out)


def files():
    for root, _, names in os.walk('.'):
        for name in names:
            if NAME.fullmatch(name):
                yield os.path.join(root, name)


def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <edid-decode> [jobs]', file=sys.stderr)
        sys.exit(1)
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    with Pool(jobs, init, (sys.argv[1],)) as pool:
        for _ in pool.imap_unordered(regenerate, files(), chunksize=256):
            pass


if __name__ == '__main__':
    main()
