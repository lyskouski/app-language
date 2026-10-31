# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

# Generates python3-modules.json (Flatpak module with pinned PyPI sources) from requirements.txt:
# > cd linux-flatpak
# > python3 generate_python_modules.py

import json
import sys
import urllib.request
from pathlib import Path

PYTHON_TAG = 'cp314'
ARCHES = ['x86_64', 'aarch64']
SDIST_PACKAGES = {'kivy', 'pillow', 'cffi', 'msgpack', 'audioop-lts'}
# Build-time only, installed before the sdist packages (pip does not order them with --no-build-isolation).
BUILD_PACKAGES = ['cython', 'pybind11']

ROOT = Path(__file__).parent
PIP_INSTALL = (
    'pip3 install --verbose --prefix=${FLATPAK_DEST} '
    '--no-index --find-links="file://${PWD}" --no-build-isolation --ignore-installed'
)


def read_requirements(path):
    pins = []
    for line in path.read_text().splitlines():
        line = line.split('#', 1)[0].strip()
        if line:
            name, version = line.split('==')
            pins.append((name.strip(), version.strip()))
    return pins


def fetch_release(name, version):
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json') as response:
        return json.load(response)['urls']


def source(entry, arch=None):
    result = {'type': 'file', 'url': entry['url'], 'sha256': entry['digests']['sha256']}
    if arch:
        result['only-arches'] = [arch]
    return result


def wheel_tags(filename):
    _, _, python, abi, platform = filename[:-len('.whl')].rsplit('-', 4)
    return python.split('.'), abi.split('.'), platform.split('.')


def is_universal(filename):
    _, abi, platform = wheel_tags(filename)
    return 'none' in abi and 'any' in platform


def is_arch_wheel(filename, arch):
    python, abi, platform = wheel_tags(filename)
    if not any(tag.startswith('manylinux') and tag.endswith(f'_{arch}') for tag in platform):
        return False
    return (PYTHON_TAG in python and PYTHON_TAG in abi) or 'abi3' in abi


def select_sources(name, version):
    files = fetch_release(name, version)
    if name.lower() in SDIST_PACKAGES:
        sdists = [f for f in files if f['packagetype'] == 'sdist']
        if not sdists:
            sys.exit(f'No sdist for {name}=={version}')
        return [source(sdists[0])]

    wheels = [f for f in files if f['packagetype'] == 'bdist_wheel']
    universal = [f for f in wheels if is_universal(f['filename'])]
    if universal:
        return [source(universal[0])]

    sources = []
    for arch in ARCHES:
        matches = sorted((f for f in wheels if is_arch_wheel(f['filename'], arch)), key=lambda f: f['filename'])
        if not matches:
            sys.exit(f'No {PYTHON_TAG} wheel for {name}=={version} ({arch})')
        sources.append(source(matches[-1], arch))
    return sources


def main():
    pins = read_requirements(ROOT / 'requirements.txt')
    sources = []
    for name, version in pins:
        print(f'{name}=={version}', file=sys.stderr)
        sources.extend(select_sources(name, version))

    build = [f'{name}=={version}' for name, version in pins if name in BUILD_PACKAGES]
    runtime = [f'{name}=={version}' for name, version in pins if name not in BUILD_PACKAGES]
    module = {
        'name': 'python3-modules',
        'buildsystem': 'simple',
        # Kivy 2.3.0 assigns GL function pointers with mismatched const qualifiers, an error since GCC 14
        'build-options': {'cflags': '-Wno-error=incompatible-pointer-types'},
        'build-commands': [
            f'{PIP_INSTALL} {" ".join(build)}',
            f'{PIP_INSTALL} {" ".join(runtime)}',
        ],
        'cleanup': ['/bin/cython*', '/bin/cygdb', '/lib/python3*/site-packages/Cython*', '/lib/python3*/site-packages/pyximport',
                    '/bin/pybind11-config', '/lib/python3*/site-packages/pybind11*'],
        'sources': sources,
    }
    (ROOT / 'python3-modules.json').write_text(json.dumps(module, indent=4) + '\n')


if __name__ == '__main__':
    main()
