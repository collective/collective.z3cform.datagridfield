from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from zope.configuration import xmlconfig


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):

        import five.grok
        xmlconfig.file('meta.zcml', five.grok,
                       context=configurationContext)

        import collective.z3cform.datagridfield
        xmlconfig.file(
            'configure.zcml',
            collective.z3cform.datagridfield,
            context=configurationContext
        )

        import collective.z3cform.datagridfield_demo
        xmlconfig.file(
            'configure.zcml',
            collective.z3cform.datagridfield_demo,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'collective.z3cform.datagridfield:default')


FIXTURE = Fixture()
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='collective.z3cform.datagridfield:Functional',
)
