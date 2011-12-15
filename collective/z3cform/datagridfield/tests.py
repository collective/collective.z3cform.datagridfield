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


from zope.publisher.browser import TestRequest
from zope.interface import alsoProvides
from zope.interface import implements
from plone.app.z3cform.interfaces import IPloneFormLayer
from Products.Five.utilities.marker import mark
from plone.z3cform.interfaces import IWrappedForm
from collective.z3cform.datagridfield_demo.testdata import EditForm, IPerson



class RelationsTestCase(ptc.PloneTestCase):
    layer = layer

    def afterSetUp(self):
        pass

    def test_relation(self):
        request = TestRequest()
        alsoProvides(request, IPloneFormLayer)
        alsoProvides(self.portal, IPerson)
        
        form = EditForm(self.portal, request)
        mark(form, IWrappedForm)
        html = form()
        pass


def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.z3cform.datagridfield',
            test_class=TestCase),

        unittest.makeSuite(RelationsTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
