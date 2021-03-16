# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        return [
            "collective.z3cform.datagridfield:uninstall",
            "collective.z3cform.datagridfield.upgrades:2",
            "collective.z3cform.datagridfield.upgrades:3",
        ]
