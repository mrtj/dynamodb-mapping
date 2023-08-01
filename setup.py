#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["boto3"]

test_requirements = [
    "pytest>=3",
    "pytest-mock>=3",
]

setup(
    author="Janos Tolgyesi",
    author_email="janos.tolgyesi@gmail.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="A Python dictionary-like interface for an Amazon DynamoDB table.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="dynamodb_mapping",
    name="dynamodb_mapping",
    packages=find_packages(include=["dynamodb_mapping", "dynamodb_mapping.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/mrtj/dynamodb_mapping",
    version="0.1.0",
    zip_safe=False,
)
