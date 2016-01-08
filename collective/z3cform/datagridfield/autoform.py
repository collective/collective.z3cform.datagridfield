"""

    Taken from http://pydoc.net/jyu.formwidget.object/1.0b7/jyu.formwidget.object.autoform

    Adds subform support for plone.autoform and plone.form.directives.

"""


# from five import grok

from zope.interface import Interface, implements
from zope.component import adapts
import zope.interface

from plone.autoform.interfaces import IAutoExtensibleForm
from plone.autoform.form import AutoExtensibleForm

from z3c.form import action
from z3c.form.interfaces import\
    ISubformFactory, IFormLayer, IObjectWidget, IMultipleErrors
from z3c.form.error import MultipleErrorViewSnippet
from z3c.form.object import ObjectSubForm, SubformAdapter

from zope.i18nmessageid import Message


class AutoExtensibleSubForm(AutoExtensibleForm, ObjectSubForm):

    @property
    def schema(self):
        return self.__parent__.field.schema

    def updateActions(self):
        self.actions = action.Actions(self.__parent__, self.request, None)

    def refreshActions(self):
        pass

    def updateWidgets(self):
        #AutoExtensibleForm.updateWidgets(self)
        ObjectSubForm.updateWidgets(self)

    def update(self):
        """
        """

        # This is awful hack but I am not sure
        # how otherwise we can get the parent
        # call chain work correctly with
        # both zope.interface.Interface schemas
        # and plone.directives.form.SchemaForm schemas.
        # This might not be 100% but worked when tested with
        # plain and grokked form.
        rowSchema = self.__parent__.field.schema

        if u'plone.autoform.widgets' in rowSchema.getTaggedValueTags():
            AutoExtensibleForm.update(self)
            self.setupFields()
        else:
            # zope.interface.Interface path
            ObjectSubForm.update(self)

    def updateFields(self):
        self.updateFieldsFromSchemata()
        super(AutoExtensibleSubForm, self).updateFields()


class AutoExtensibleSubformAdapter(SubformAdapter):
    """Most basic-default subform factory adapter"""
    adapts(Interface,   # widget value
           IFormLayer,  # request
           Interface,   # widget context
           IAutoExtensibleForm,  # form
           IObjectWidget,  # widget
           Interface,   # field
           Interface)   # field.schema
    implements(ISubformFactory)

    factory = AutoExtensibleSubForm


# XXX: The following controversial and may have side effects.
# Its only purpose is to hide redundant error messages. Every
# error within a subform seem to be rendered both for
# the subform and for the individual field.


class MultipleErrorViewSnippetWithMessage(MultipleErrorViewSnippet):
    adapts(
        IMultipleErrors, None, None, None, IAutoExtensibleForm, None)

    def render(self):
        return Message(u"There were some errors.", domain="z3c.form")