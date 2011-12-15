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
from zope.annotation.interfaces import IAttributeAnnotatable
from z3c.relationfield import RelationValue


class RelationsTestCase(ptc.PloneTestCase):
    layer = layer

    def afterSetUp(self):
        pass

    def test_relationchoice(self):
        
        assert not hasattr(self.portal.aq_base, 'address')

        request = TestRequest(form={'form.widgets.mytitle': 'This is my title',
                                    'form.widgets.address.0.widgets.anothertitle': 'This is another title',
                                    'form.widgets.address.0.widgets.link': ['/Plone/news', ]})
        alsoProvides(request, IPloneFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        alsoProvides(self.portal, IPerson)
        
        form = EditForm(self.portal, request)
        mark(form, IWrappedForm)

        form.update()
        form.render()
        
        # Fake submitting. Plone redirects after a successful save.
        data, errors = form.extractData()
        form.applyChanges(data)

        # address should be a list of dicts, each containing a RelationValue for the link
        assert hasattr(self.portal.aq_base, 'address')
        assert isinstance(self.portal.address, list)
        for f in self.portal.address:
            assert isinstance(f['link'], RelationValue)

    def test_relationlist(self):
        
        assert not hasattr(self.portal.aq_base, 'address')

        request = TestRequest(form={'form.widgets.mytitle': 'This is my title',
                                    'form.widgets.address.0.widgets.anothertitle': 'This is another title',
                                    'form.widgets.address.0.widgets.links': ['/Plone/news', '/Plone/front-page' ]})
        alsoProvides(request, IPloneFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        alsoProvides(self.portal, IPerson)
        
        form = EditForm(self.portal, request)
        mark(form, IWrappedForm)

        form.update()
        form.render()
        
        # Fake submitting. Plone redirects after a successful save.
        data, errors = form.extractData()
        form.applyChanges(data)

        # address should be a list of dicts, each containing a RelationValue for the link
        assert hasattr(self.portal.aq_base, 'address')
        assert isinstance(self.portal.address, list)
        for f in self.portal.address:
            for l in f['links']:
                assert isinstance(l, RelationValue)



def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.z3cform.datagridfield',
            test_class=TestCase),

        unittest.makeSuite(RelationsTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
