"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from five import grok

from zope.interface import Interface
from zope import schema

from z3c.form import field, button
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE

from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory


class IAddress(Interface):
    address_type = schema.Choice(
        title = u'Address Type', required=True,
        values=[u'Work', u'Home'])
    line1 = schema.TextLine(
        title = u'Line 1', required=True)
    line2 = schema.TextLine(
        title = u'Line 2', required=False)
    city = schema.TextLine(
        title = u'City / Town', required=True)
    country = schema.TextLine(
        title = u'Country', required=True)

# Note: when using a dict, it is still an object - A schema.Dict would be
#       expected to contain some schemas. We are using an object implemented
#       as a dict

class IPerson(Interface):
    name = schema.TextLine(title=u'Name', required=True)
    address = schema.List(title=u'Addresses',
        value_type=schema.Object(title=u'Address', schema=IAddress),
        required=True)

TESTDATA = {
    'name': 'MY NAME',
    'address': [
           {'address_type': 'Work',
            'line1': 'My Office',
            'line2': 'Big Office Block',
            'city': 'Mega City',
            'country': 'The Old Sod'},
           {'address_type': 'Home',
            'line1': 'Home Sweet Home',
            'line2': 'Easy Street',
            'city': 'Burbs',
            'country': 'The Old Sod'}
    ]}

class EditForm(form.EditForm):
    label = u'Simple Form'

    grok.context(Interface)
    grok.name('demo-collective.z3cform.datagrid')

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        return TESTDATA

    @button.buttonAndHandler(u'Save', name='save')
    def handleSave(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        context = self.getContent()
        for k, v in data.items():
            context[k] = v

    def updateActions(self):
        """Bypass the baseclass editform - it causes problems"""
        super(form.EditForm, self).updateActions()

class EditForm2(EditForm):
    label = u'Hide the Row Manipulators'

    grok.name('demo-collective.z3cform.datagrid-no-manipulators')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm2, self).updateWidgets()
        self.widgets['address'].allow_insert = False
        self.widgets['address'].allow_delete = False

class EditForm3(EditForm):
    label = u'Disable Auto-append'

    grok.name('demo-collective.z3cform.datagrid-no-auto-append')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm3, self).updateWidgets()
        self.widgets['address'].auto_append = False

class EditForm4(EditForm):
    label = u'Omit a column'

    grok.name('demo-collective.z3cform.datagrid-no-country')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm4, self).updateWidgets()
        self.widgets['address'].columns = [c for c in self.widgets['address'].columns if c['name'] != 'country']

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('country')

class EditForm5(EditForm):
    label = u'Configure Subform Widgets'

    grok.name('demo-collective.z3cform.datagrid-column-widths')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['line1'].size = 40
        widgets['line2'].size = 40
        widgets['city'].size = 20
        widgets['country'].size = 10

class EditForm6(EditForm):
    label = u'Hide a Column'

    grok.name('demo-collective.z3cform.datagrid-hidden-column')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets['city'].mode = HIDDEN_MODE

    def updateWidgets(self):
        # This one hides the column title
        super(EditForm6, self).updateWidgets()
        self.widgets['address'].columns[3]['mode']  = HIDDEN_MODE

class EditForm7(EditForm):
    label = u'Table is read-only, cells editable'

    grok.name('demo-collective.z3cform.datagrid-read-only')

    def updateWidgets(self):
        super(EditForm7, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE

class EditForm8(EditForm):
    label = u'Table and cells are read-only'

    grok.name('demo-collective.z3cform.datagrid-read-only2')

    def updateWidgets(self):
        super(EditForm8, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE
        for row in self.widgets['address'].widgets:
            for widget in row.subform.widgets.values():
                widget.mode = DISPLAY_MODE


