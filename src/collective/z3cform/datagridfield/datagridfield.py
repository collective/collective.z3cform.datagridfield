# -*- coding: utf-8 -*-
"""
    Implementation of the widget
"""
from Acquisition import aq_parent
from collective.z3cform.datagridfield import _
from collective.z3cform.datagridfield.interfaces import IDataGridFieldWidget
from plone.autoform.base import AutoFields
from plone.autoform.interfaces import MODES_KEY
from z3c.form import interfaces
from z3c.form.browser.multi import MultiWidget
from z3c.form.browser.object import ObjectWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from z3c.form.error import MultipleErrors
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import NO_VALUE
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFieldNames
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IField
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ValidationError

import logging
import lxml


logger = logging.getLogger(__name__)


@implementer(IDataGridFieldWidget)
class DataGridFieldWidget(MultiWidget):
    """This grid should be applied to an schema.List item which has
    schema.Object and an interface"""

    allow_insert = True
    allow_delete = True
    allow_reorder = False
    auto_append = True
    display_table_css_class = "datagridwidget-table-view"
    input_table_css_class = "table table-striped"

    klass = "datagridfield"

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, value):
        """
        The field information is passed to the widget after it is
        initialised.  Use this call to initialise the column
        definitions.
        """
        self._field = value
        schema = self._field.value_type.schema

        fieldmodes = {}
        try:
            modes_tags = schema.getTaggedValue(MODES_KEY)
        except KeyError:
            pass
        else:
            for __, fieldname, mode in modes_tags:
                fieldmodes[fieldname] = mode

        self.columns = []
        for name, field in getFieldsInOrder(schema):
            col = {
                "name": name,
                "label": field.title,
                "description": field.description,
                "required": field.required,
                "mode": fieldmodes.get(name, None),
            }
            self.columns.append(col)

    def createObjectWidget(self, idx):
        """
        Create the widget which handles individual rows.

        Allow row-widget overriding for more specific use cases.
        """

        valueType = self.field.value_type

        if IObject.providedBy(valueType):
            widget = DataGridFieldObjectWidgetFactory(valueType, self.request)
            widget.setErrors = idx not in ["TT", "AA"]
        else:
            widget = getMultiAdapter((valueType, self.request), interfaces.IFieldWidget)

        return widget

    def getWidget(self, idx):
        """Create the object widget. This is used to avoid looking up
        the widget.
        """

        widget = self.createObjectWidget(idx)

        # widgets.line1 -> form-widgets-address-0-widgets-line1
        self.setName(widget, idx)

        widget.__parent__ = self

        widget.mode = self.mode
        widget.klass = "datagridwidget-row"
        # set widget.form (objectwidget needs this)
        # and widget.parentForm (plone.app.widget.utils.get_widget_form)
        if interfaces.IFormAware.providedBy(self):
            widget.form = self.form
            widget.parentForm = self.form
            alsoProvides(widget, interfaces.IFormAware)
        widget.update()
        return widget

    def name_prefix(self):
        return self.prefix

    def id_prefix(self):
        return self.prefix.replace(".", "-")

    def updateWidgets(self):
        if self.mode == INPUT_MODE:
            # filter out any auto append or template rows
            # these are not "real" elements of the MultiWidget
            # and confuse updateWidgets method if len(self.widgets) changes
            # This is relevant for nested datagridfields.
            self.widgets = [
                w
                for w in self.widgets
                if not (w.id.endswith("AA") or w.id.endswith("TT"))
            ]

        # if the field has configuration data set - copy it
        super().updateWidgets()

        if self.mode == INPUT_MODE:
            if self.auto_append:
                # If we are doing 'auto-append', then a blank row
                # needs to be added
                widget = self.getWidget("AA")
                widget.klass = "datagridwidget-row auto-append"
                self.widgets.append(widget)

            if self.auto_append or self.allow_insert:
                # If we can add rows, we need a template row
                template = self.getWidget("TT")
                template.klass = "datagridwidget-row datagridwidget-empty-row"
                self.widgets.append(template)

    @property
    def counterMarker(self):
        # Override this to exclude template line and auto append line
        counter = len(self.widgets)
        if self.auto_append:
            counter -= 1
        if self.auto_append or self.allow_insert:
            counter -= 1
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counterName,
            counter,
        )

    def _includeRow(self, name):
        if self.mode == INPUT_MODE:
            if not name.endswith("AA") and not name.endswith("TT"):
                return True
            if name.endswith("AA"):
                return self.auto_append
            if name.endswith("TT"):
                return self.auto_append or self.allow_insert
        else:
            return not name.endswith("AA") and not name.endswith("TT")


@adapter(IField, IFormLayer)
@implementer(interfaces.IFieldWidget)
def DataGridFieldWidgetFactory(field, request):
    """IFieldWidget factory for DataGridFieldWidget."""
    return FieldWidget(field, DataGridFieldWidget(request))


# BBB
DataGridFieldFactory = DataGridFieldWidgetFactory


PAT_XPATH = "//*[contains(concat(' ', normalize-space(@class), ' '), ' pat-')]"


class DataGridFieldObjectWidget(AutoFields, ObjectWidget):
    def isInsertEnabled(self):
        return self.__parent__.allow_insert

    def isDeleteEnabled(self):
        return self.__parent__.allow_delete

    def isReorderEnabled(self):
        return self.__parent__.allow_reorder

    # plone.autoform

    @property
    def schema(self):
        return self.field.schema

    def setupFields(self):
        self.updateFieldsFromSchemata()

    # ObjectWidget API

    def getObject(self, value):
        # our object is the dict value
        return value

    @property
    def value(self):
        # value (get) cannot raise an exception, then we return
        # insane values
        try:
            return self.extract()
        except MultipleErrors:
            value = {}
            active_names = self.fields.keys()
            for name in getFieldNames(self.schema):
                if name not in active_names:
                    continue
                widget = self.widgets[name]
                value[name] = widget.value
            return value

    @value.setter
    def value(self, value):
        self._value = value

        if value is NO_VALUE:
            return

        # ensure that we apply our new values to the widgets
        active_names = self.fields.keys()
        for name, fieldset_field in self.schema.namesAndDescriptions():
            if fieldset_field.readonly:
                continue
            if name in active_names:
                if isinstance(value, dict):
                    v = value.get(name, NO_VALUE)
                else:
                    v = getattr(value, name, NO_VALUE)
                if v is NO_VALUE:
                    continue
                widget = self.widgets[name]
                widget.value = v

    def updateWidgets(self, *args, **kwargs):
        super().updateWidgets(*args, **kwargs)

        # Tell the "cell"-widget the "mode" of it's column,
        # so that plone.autoform.directives.mode works on the cell.
        for column_info in aq_parent(self).columns:
            if column_info["name"] not in self.widgets:
                # skip readonly widgets
                continue
            if self.id.endswith("AA") or self.id.endswith("TT"):
                # ignore required on auto-append and template rows
                self.widgets[column_info["name"]].required = False
            if column_info["mode"] is not None:
                self.widgets[column_info["name"]].mode = column_info["mode"]

    def extractRaw(self, setErrors=True):
        # override ObjectWidget extractRaw
        self.widgets.setErrors = setErrors
        return self.widgets.extractRaw()

    def render(self):
        """See z3c.form.interfaces.IWidget."""
        html = super().render()
        if "datagridwidget-empty-row" in self.klass or "auto-append" in self.klass:
            # deactivate patterns
            fragments = lxml.html.fragments_fromstring(html)
            html = ""
            for tree in fragments:
                for el in tree.xpath(PAT_XPATH):
                    if ".TT." in el.attrib.get("name", ""):
                        el.attrib["class"] = el.attrib["class"].replace(
                            "pat-", "dgw-disabled-pat-"
                        )
                html += lxml.html.tostring(tree, encoding="unicode") + "\n"
        return html

    def label_add_record(self):
        return _(
            "add_record_label",
            default="Add ${type}",
            mapping={"type": self.field.title},
        )


@adapter(IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def DataGridFieldObjectWidgetFactory(field, request):
    """IFieldWidget factory for DataGridFieldObjectWidget."""
    return FieldWidget(field, DataGridFieldObjectWidget(request))


# BBB
DataGridFieldObjectFactory = DataGridFieldObjectWidgetFactory


@implementer(IValidator)
@adapter(
    Interface,
    Interface,
    Interface,  # Form
    IList,  # field
    DataGridFieldWidget,  # widgets
)
class DataGridValidator(SimpleFieldValidator):
    """
    I am crippling this validator - I return a list of
    dictionaries. If I don't cripple this it will fail because the
    return type is not of the correct object type. For stronger
    typing replace both this and the converter
    """

    def validate(self, value, force=False):
        """
        Don't validate the table - however, if there is a cell
        error, make sure that the table widget shows it.
        """
        for row in self.widget.widgets:
            if row.id.endswith("AA") or row.id.endswith("TT"):
                # ignore auto appended and template widgets
                continue
            # check each column
            for col in row.widgets.values():
                if hasattr(col, "error") and col.error:
                    raise ValueError(col.label)
        return None
