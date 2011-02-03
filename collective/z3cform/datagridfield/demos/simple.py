"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from five import grok

from zope.interface import Interface
from zope import schema

from z3c.form import field
from z3c.form.widget import FieldWidget

from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DataGridField


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

class IPerson(Interface):
    name = schema.TextLine(title=u'Name', required=True)
    address = schema.List(title=u'Addresses',
        value_type=schema.Object(title=u'Address', schema=IAddress),
        required=True)

class EditForm(form.EditForm):
    label = u'This is a simple, default layout'

    grok.context(Interface)
    grok.name('demo-simple-edit-form')

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        return {
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


def DataGridFieldFactory2(field, request):
    """Define a factory which produces a version which does not allow insert / delete"""
    dgf = DataGridField(request)
    dgf.allow_insert = False
    dgf.allow_delete = False
    return FieldWidget(field, dgf)

class EditForm2(EditForm):
    label = u'This form has the insert and delete row options removed'

    grok.name('demo-edit-form-no-row-manipulators')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory2

def DataGridFieldFactory3(field, request):
    """Define a factory which produces a version which does not allow insert / delete"""
    dgf = DataGridField(request)
    dgf.auto_append = False
    return FieldWidget(field, dgf)


class EditForm3(EditForm):
    label = u'This form has the auto-append row options removed'

    grok.name('demo-edit-form-no-auto-append')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory3

#### THIS ONE ONE NOT WORKING
#### Widgets already initialised when this code is called

class EditForm4(EditForm):
    label = u'This form has the country column removed - NOT WORKING'

    grok.name('demo-edit-form-no-country')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('country')

class EditForm5(EditForm):
    label = u'This form has column widths configured'

    grok.name('demo-edit-form-column-widths')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['line1'].size = 40
        widgets['line2'].size = 40
        widgets['city'].size = 20
        widgets['city'].size = 10


class EditForm6(EditForm):
    label = u'This form has hidden the city column'

    grok.name('demo-edit-form-hidden-column')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets['city'].mode = 'hidden'

    def updateWidgets(self):
        # This one hides the column title
        super(EditForm6, self).updateWidgets()
        self.widgets['address'].columns[3]['mode']  = 'hidden'

