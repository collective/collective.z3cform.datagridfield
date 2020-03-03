# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    # zest.releaser needs version here for now
    version='1.5.3',

    # thanks to this bug
    # https://github.com/pypa/setuptools/issues/1136
    # we need one line in here:
    package_dir={"": "src"},

    # see setup.cfg

    extras_require={
        'test': [
            'plone.app.robotframework[debug]',
        ],
    },
)
