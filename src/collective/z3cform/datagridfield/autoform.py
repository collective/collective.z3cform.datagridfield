"""

    Taken from
    http://pydoc.net/jyu.formwidget.object/1.0b7/jyu.formwidget.object.autoform

    Adds subform support for plone.autoform.

"""

from lxml import etree
from plone.autoform.interfaces import IAutoExtensibleForm
from plone.autoform.widgets import WidgetExportImportHandler
from plone.supermodel.utils import noNS
from z3c.form.browser.interfaces import IHTMLFormElement
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


class DGFExportImportHandler(WidgetExportImportHandler):
    # XML exportimport handler for DataGridFieldWidget

    def read(self, widgetNode, params):
        super().read(widgetNode, params)
        # we simply add DGF widget attributes here
        for attributeName in (
            "allow_insert",
            "allow_delete",
            "allow_reorder",
            "auto_append",
        ):
            # translate boolean values
            for node in widgetNode.iterchildren():
                if noNS(node.tag) == attributeName:
                    params[attributeName] = node.text.lower() in (
                        "y",
                        "yes",
                        "true",
                        "on",
                        "1",
                    )

        for attributeName in (
            "display_table_css_class",
            "input_table_css_class",
        ):
            for node in widgetNode.iterchildren():
                if noNS(node.tag) == attributeName:
                    params[attributeName] = node.text

    def write(self, widgetNode, params):
        super().write(widgetNode, params)
        for attributeName in (
            "allow_insert",
            "allow_delete",
            "allow_reorder",
            "auto_append",
            "display_table_css_class",
            "input_table_css_class",
        ):
            child = etree.Element(attributeName)
            child.text = params.get(attributeName, "")
            widgetNode.append(child)


DGFExportImportHandlerFactory = DGFExportImportHandler(IHTMLFormElement)
