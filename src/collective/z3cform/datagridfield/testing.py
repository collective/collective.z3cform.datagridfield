# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.z3cform.datagridfield
        self.loadZCML(package=collective.z3cform.datagridfield)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'collective.z3cform.datagridfield:default')


FIXTURE = Fixture()
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER_FIXTURE,
           ),
    name='collective.z3cform.datagridfield:Functional',
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='collective.z3cform.datagridfield:AcceptanceTesting',
)
