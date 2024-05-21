from setuptools import setup, find_packages

setup(
    name='story-protocol-python-sdk',
    version='0.1.0',
    packages=find_packages(where='src', exclude=["tests"]),
    package_dir={'': 'src'},
    install_requires=[
        'web3>=5.0.0',
        'pytest',
        'python-dotenv'
    ],
    url='https://github.com/aandrewchung/python-sdk/tree/andrew/pip-install',
    license='MIT',
    author='Andrew Chung',
    author_email='andrew@storyprotocol.xyz',
    description='A Python SDK for interacting with the Story Protocol.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
