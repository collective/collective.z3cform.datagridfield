# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    # zest.releaser needs version here for now
    version="3.0.2",
    # thanks to this bug
    # https://github.com/pypa/setuptools/issues/1136
    # we need one line in here:
    package_dir={"": "src"},
    # some options for pyroma here
    python_requires=">=3.8",
)
