import re, os
from setuptools import setup

version_type = os.getenv('VERSION_TYPE')

with open('setup.py', 'r') as f:
    setup_py = f.read()

version = re.search(r"version='(\d+\.\d+\.\d+)'", setup_py).group(1)
major, minor, patch = map(int, version.split('.'))

if version_type == 'major':
    major += 1
    minor = 0
    patch = 0
elif version_type == 'minor':
    minor += 1
    patch = 0
elif version_type == 'patch':
    patch += 1

new_version = f"{major}.{minor}.{patch}"

with open('setup.py', 'w') as f:
    f.write(re.sub(r"version='(\d+\.\d+\.\d+)'", f"version='{new_version}'", setup_py))

