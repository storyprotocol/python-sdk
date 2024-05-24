import re
from setuptools import setup

with open('setup.py', 'r') as f:
    setup_py = f.read()

version = re.search(r"version='(\d+\.\d+\.\d+)'", setup_py).group(1)
major, minor, patch = map(int, version.split('.'))

if minor == 9:
    if patch == 9:
        major += 1
        minor = 0
        patch = 0
    else:
        patch += 1
elif patch == 9:
    patch = 0
    minor += 1
else:
    patch += 1

new_version = f"{major}.{minor}.{patch}"

with open('setup.py', 'w') as f:
    f.write(re.sub(r"version='(\d+\.\d+\.\d+)'", f"version='{new_version}'", setup_py))

