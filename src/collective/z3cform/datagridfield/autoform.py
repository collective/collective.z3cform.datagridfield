# -*- coding: utf-8 -*-
"""

    Taken from
    http://pydoc.net/jyu.formwidget.object/1.0b7/jyu.formwidget.object.autoform

    Adds subform support for plone.autoform.

"""
from plone.autoform.interfaces import IAutoExtensibleForm
from z3c.form.error import MultipleErrorViewSnippet
from z3c.form.interfaces import IMultipleErrors
from zope.component import adapter
from zope.i18nmessageid import Message


# XXX: The following controversial and may have side effects.
# Its only purpose is to hide redundant error messages. Every
# error within a subform seem to be rendered both for
# the subform and for the individual field.


@adapter(IMultipleErrors, None, None, None, IAutoExtensibleForm, None)
class MultipleErrorViewSnippetWithMessage(MultipleErrorViewSnippet):
    def render(self):
        return Message("There were some errors.", domain="z3c.form")
