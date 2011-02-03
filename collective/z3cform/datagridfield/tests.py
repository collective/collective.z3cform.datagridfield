import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer

ptc.setupPloneSite()


class Layer(BasePTCLayer):

    def afterSetUp(self):
        # Install the example.conference product
        fiveconfigure.debug_mode = True
        self.addProfile('collective.z3cform.datagridfield:default')
        fiveconfigure.debug_mode = False

layer = Layer([ptc_layer])


class TestCase(ptc.PloneTestCase):
    layer = layer


def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.z3cform.datagridfield',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
