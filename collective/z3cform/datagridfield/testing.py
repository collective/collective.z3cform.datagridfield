from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting


class Fixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.z3cform.datagridfield
        self.loadZCML(package=collective.z3cform.datagridfield)

        import collective.z3cform.datagridfield_demo
        self.loadZCML(package=collective.z3cform.datagridfield_demo)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'collective.z3cform.datagridfield:default')


FIXTURE = Fixture()
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='collective.z3cform.datagridfield:Functional',
)
