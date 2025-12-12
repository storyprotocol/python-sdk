from setuptools import find_packages, setup

# python setup.py sdist
# twine upload dist/*

setup(
    name="story_protocol_python_sdk",
    version="0.3.17",
    packages=find_packages(where="src", exclude=["tests"]),
    package_dir={"": "src"},
    install_requires=["web3>=7.0.0", "pytest", "python-dotenv", "base58"],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "ruff",
            "pre-commit",
            "coverage",
            "pytest-html",
        ],
    },
    include_package_data=True,  # Ensure package data is included
    package_data={"story_protocol_python_sdk": ["py.typed"]},
    url="https://github.com/storyprotocol/python-sdk",
    license="MIT",
    author="Andrew Chung",
    author_email="andrew@storyprotocol.xyz",
    description="A Python SDK for interacting with Story.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
