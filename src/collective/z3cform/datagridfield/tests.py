# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield.testing import FUNCTIONAL_TESTING
from collective.z3cform.datagridfield.testing import ACCEPTANCE_TESTING
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered

import doctest
import os
import pprint
import robotsuite
import unittest


OPTIONFLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                'browser.rst',
                package='collective.z3cform.datagridfield',
                optionflags=OPTIONFLAGS,
                globs={'pprint': pprint.pprint, }
            ),
            layer=FUNCTIONAL_TESTING
        )
    ])

    current_dir = os.path.abspath(os.path.dirname(__file__))
    test_dir = os.path.join(current_dir, 'tests')
    robot_dir = os.path.join(test_dir, 'robot')
    robot_tests = [
        os.path.join('tests/robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.robot') and doc.startswith('test_')
    ]
    for robot_test in robot_tests:
        robottestsuite = robotsuite.RobotTestSuite(robot_test)
        robottestsuite.level = ROBOT_TEST_LEVEL
        suite.addTests([
            layered(
                robottestsuite,
                layer=ACCEPTANCE_TESTING,
            ),
        ])

    return suite
