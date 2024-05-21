from setuptools import setup, find_packages

setup(
    name='story-protocol-python-sdk',
    version='1.0.0',
    description='A Python SDK for interacting with the Story Protocol',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Andrew Chung',
    author_email='andrew@storyprotocol.xyz',
    url='https://github.com/aandrewchung/python-sdk/tree/andrew/pip-install',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'web3>=5.0.0',
        'pytest',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'generate-client=scripts.generate_client:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
