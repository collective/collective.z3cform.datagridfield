# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)
default_profile = 'profile-collective.z3cform.datagridfield:default'


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'collective.z3cform.datagridfield:uninstall',
        ]


def to_2(context):
    """
    """
    logger.info('Upgrading collective.z3cform.datagridfield to version 2')
    context.runAllImportStepsFromProfile(
        'profile-collective.z3cform.datagridfield:to_2')
    context.runImportStepFromProfile(default_profile, 'plone.app.registry')
    logger.info('Reinstalled registry')
