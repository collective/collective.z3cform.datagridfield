import doctest
import unittest2 as unittest
import pprint
from plone.testing import layered
from collective.z3cform.datagridfield.testing import FUNCTIONAL_TESTING

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)


from zope.publisher.browser import TestRequest
from zope.interface import alsoProvides
from plone.app.z3cform.interfaces import IPloneFormLayer
from Products.Five.utilities.marker import mark
from plone.z3cform.interfaces import IWrappedForm
from collective.z3cform.datagridfield_demo.browser.simple import EditForm, IPerson
from zope.annotation.interfaces import IAttributeAnnotatable
from z3c.relationfield import RelationValue


class RelationsTestCase(unittest.TestCase):
    layer = FUNCTIONAL_TESTING

    def afterSetUp(self):
        portal = self.layer['portal']
        from zope.intid.interfaces import IIntIds
        from zope.component import getUtility

        intids = getUtility(IIntIds)
        intids.register(portal.news)
        intids.register(portal['front-page'])

    def test_relationchoice(self):
        portal = self.layer['portal']

        assert not hasattr(portal.aq_base, 'address')

        request = TestRequest(form={'form.widgets.mytitle': 'This is my title',
                                    'form.widgets.address.0-empty-marker': '1',
                                    'form.widgets.address.0.widgets.anothertitle': 'This is another title',
                                    'form.widgets.address.0.widgets.link': ['/plone/news'],
                                    'form.widgets.address.0.widgets.link-empty-marker': '1',
                                    'form.widgets.address.count': '1',
                                    })
        alsoProvides(request, IPloneFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        alsoProvides(portal, IPerson)

        form = EditForm(portal, request)
        mark(form, IWrappedForm)

        form.update()
        form.render()

        # Fake submitting. Plone redirects after a successful save.
        data, errors = form.extractData()
        form.applyChanges(data)

        # address should be a list of dicts, each containing a RelationValue for the link
        assert hasattr(portal.aq_base, 'address')
        assert isinstance(portal.address, list)
        assert len(portal.address) > 0
        for f in portal.address:
            assert isinstance(f['link'], RelationValue)

    def test_relationlist(self):
        portal = self.layer['portal']

        assert not hasattr(portal.aq_base, 'address')

        request = TestRequest(form={'form.widgets.mytitle': 'This is my title',
                                    'form.widgets.address.0-empty-marker': '1',
                                    'form.widgets.address.0.widgets.anothertitle': 'This is another title',
                                    'form.widgets.address.0.widgets.links': ['/plone/news', '/plone/front-page'],
                                    'form.widgets.address.0.widgets.links-empty-marker': '1',
                                    'form.widgets.address.count': '1',
                                    })
        alsoProvides(request, IPloneFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        alsoProvides(portal, IPerson)

        form = EditForm(portal, request)
        mark(form, IWrappedForm)

        form.update()
        form.render()

        # Fake submitting. Plone redirects after a successful save.
        data, errors = form.extractData()
        form.applyChanges(data)

        # address should be a list of dicts, each containing a RelationValue for the link
        assert hasattr(portal.aq_base, 'address')
        assert isinstance(portal.address, list)
        assert len(portal.address) > 0
        for f in portal.address:
            assert len(f['links']) > 0
            for l in f['links']:
                assert isinstance(l, RelationValue)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('browser.txt',
                                     optionflags=OPTIONFLAGS,
                                     globs={'pprint': pprint.pprint,
                                            }
                                     ),
                layer=FUNCTIONAL_TESTING),
        unittest.makeSuite(RelationsTestCase)])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
