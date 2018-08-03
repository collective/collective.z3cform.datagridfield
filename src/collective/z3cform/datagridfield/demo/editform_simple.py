# -*- coding: utf-8 -*-
"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from collective.z3cform.datagridfield import BlockDataGridFieldFactory
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from datetime import datetime
from plone.autoform.directives import widget
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.interface import Interface
# Uncomment, if you want to try the relationfield
# from plone.app.vocabularies.catalog import CatalogSource
# from z3c.relationfield.schema import RelationChoice


try:
    from collective.z3cform.datetimewidget import widget_datetime
except ImportError:
    widget_datetime = None


if widget_datetime is not None:
    from z3c.form.widget import FieldWidget

    class DataGridFieldDatetimeWidget(widget_datetime.DatetimeWidget):
        # Causes grey hair because of invalid value handling
        # so we disable this for now
        show_jquerytools_dateinput = False

    def DataGridFieldDatetimeFieldWidget(field, request):
        """IFieldWidget factory for DatetimeWidget."""
        return FieldWidget(field, DataGridFieldDatetimeWidget(request))


class IAddress(Interface):
    address_type = schema.Choice(
        title=u'Address Type', required=True,
        values=[u'Work', u'Home'])
# Uncomment, if you want to try the relationfield
#    link = RelationChoice(
#        title=u"Link to content",
#        source=CatalogSource(portal_type=['Document']),
#        required=True
#    )
    line1 = schema.TextLine(
        title=u'Line 1', required=True)
    line2 = schema.TextLine(
        title=u'Line 2', required=False)
    city = schema.TextLine(
        title=u'City / Town', required=True)
    country = schema.TextLine(
        title=u'Country', required=True)
    frozenField = schema.TextLine(
        title=u'Don\'t change', readonly=True, required=True)

    # A sample integer field
    personCount = schema.Int(title=u'Persons', required=False, min=0, max=15)

    # A sample datetime field
    if widget_datetime is not None:
        widget(dateAdded=DataGridFieldDatetimeFieldWidget)
    dateAdded = schema.Datetime(title=u"Date added")

    # A sample checkbox
    billed = schema.Bool(title=u"Billed")


class IPerson(Interface):
    """
    Note: when using a dict, it is still an object - A schema.Dict would be
    expected to contain some schemas. We are using an object implemented
    as a dict
    """
    name = schema.TextLine(title=u'Name', required=True)
    address = schema.List(
        title=u'Addresses',
        value_type=DictRow(title=u'Address', schema=IAddress),
        required=True
    )


TESTDATA = {
    'name': 'MY NAME',
    'address': [
           {'address_type': 'Work',
            'line1': 'My Office',
            'line2': 'Big Office Block',
            'city': 'Mega City',
            'country': 'The Old Sod',
            'personCount': 2,
            'dateAdded': datetime(1981, 8, 17, 06, 00, 00)
            },
           {'address_type': 'Home',
            'line1': 'Home Sweet Home',
            'line2': 'Easy Street',
            'city': 'Burbs',
            'country': 'The Old Sod',
            'personCount': 4,
            'dateAdded': datetime(1981, 8, 17, 06, 00, 00)
            }
    ]}


class EditForm(form.EditForm):
    label = u'Simple Form'

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    show_note = False

    def getContent(self):
        return TESTDATA

    def dumpOutput(self, data):
        """
        Helper function to see what kind of data DGF submits.
        """
        address = data.get("address", [])

        print "Dumping out extracted addresses"
        for entry in address:
            print entry

        print "Dumping out raw HTTP POST form data"
        for k, v in self.request.form.items():
            print "%s: %s" % (k, v)

    @button.buttonAndHandler(u'Save', name='save')
    def handleSave(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.dumpOutput(data)

        context = self.getContent()
        for k, v in data.items():
            context[k] = v

    def updateActions(self):
        """Bypass the baseclass editform - it causes problems"""
        super(form.EditForm, self).updateActions()

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['address'].allow_reorder = True


class EditForm2(EditForm):
    label = u'Hide the Row Manipulators'

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm2, self).updateWidgets()
        self.widgets['address'].allow_insert = False
        self.widgets['address'].allow_delete = False


class EditForm3(EditForm):
    label = u'Disable Auto-append'

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm3, self).updateWidgets()
        self.widgets['address'].auto_append = False


class EditForm4(EditForm):
    label = u'Omit a column'

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm4, self).updateWidgets()
        self.widgets['address'].columns = [
            c for c in self.widgets['address'].columns
            if c['name'] != 'country']

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('country')


class EditForm5(EditForm):
    label = u'Configure Subform Widgets'

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['line1'].size = 40
        widgets['line2'].size = 40
        widgets['city'].size = 20
        widgets['country'].size = 10


class EditForm6(EditForm):
    label = u'Hide a Column'

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets['city'].mode = HIDDEN_MODE

    def updateWidgets(self):
        # This one hides the column title
        super(EditForm6, self).updateWidgets()
        self.widgets['address'].columns[3]['mode'] = HIDDEN_MODE


class EditForm7(EditForm):
    label = u'Table is read-only, cells editable'
    show_note = True

    def updateWidgets(self):
        super(EditForm7, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE


class EditForm8(EditForm):
    label = u'Table and cells are read-only'

    def updateWidgets(self):
        super(EditForm8, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE
        for row in self.widgets['address'].widgets:
            for wdt in row.subform.widgets.values():
                wdt.mode = DISPLAY_MODE


class EditForm9(EditForm):

    label = u'Block widgets as blocks instead of cells'

    # Because we modify fields in-place in update()
    # We need our own copy so that we don't damage other forms
    fields = field.Fields(IPerson)

    def update(self):
        # Set a custom widget for a field for this form instance only
        self.fields['address'].widgetFactory = BlockDataGridFieldFactory
        super(EditForm9, self).update()
