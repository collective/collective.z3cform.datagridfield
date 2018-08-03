# -*- coding: utf-8 -*-
"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import IDataGridField
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.interface import implementer
from zope.interface import Interface
from zope.component import adapter
from zope.schema import getFieldsInOrder
from zope.schema.fieldproperty import FieldProperty
# Uncomment, if you want to try the relationfield
# from plone.app.vocabularies.catalog import CatalogSource
# from z3c.relationfield.schema import RelationChoice


class IAddress(Interface):
    address_type = schema.Choice(
        title=u'Address Type', required=True,
        values=[u'Work', u'Home']
    )
    line1 = schema.TextLine(
        title=u'Line 1',
        required=True
    )
    line2 = schema.TextLine(
        title=u'Line 2',
        required=False
    )
    city = schema.TextLine(
        title=u'City / Town',
        required=True
    )
    country = schema.TextLine(
        title=u'Country',
        required=True
    )
# Uncomment, if you want to try the relationfield
#    link = RelationChoice(
#        title=u"Link to content",
#        source=CatalogSource(portal_type=['Document']),
#        required=False)


class AddressListField(schema.List):
    """We need to have a unique class for the field list so that we
    can apply a custom adapter."""
    pass


class IPerson(Interface):
    name = schema.TextLine(title=u'Name', required=True)
    address = AddressListField(
        title=u'Addresses',
        value_type=schema.Object(title=u'Address', schema=IAddress),
        required=True
    )


@implementer(IAddress)
class Address(object):
    address_type = FieldProperty(IAddress['address_type'])
    line1 = FieldProperty(IAddress['line1'])
    line2 = FieldProperty(IAddress['line2'])
    city = FieldProperty(IAddress['city'])
    country = FieldProperty(IAddress['country'])
# Uncomment, if you want to try the relationfield
#    link = FieldProperty(IAddress['link'])

    # allow getSource to proceed
    _Modify_portal_content_Permission = ('Anonymous', )

    def __init__(self, address_type=None, line1=None, line2=None, city=None,
                 country=None, link=None):
        self.address_type = address_type
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.country = country
        self.link = link


class AddressList(list):
    pass


@implementer(IPerson)
class Person(object):
    name = FieldProperty(IPerson['name'])
    address = FieldProperty(IPerson['address'])

    # allow getSource to proceed
    _Modify_portal_content_Permission = ('Anonymous', )

    def __init__(self, name=None, address=None):
        self.name = name
        self.address = address


TESTDATA = Person(
    name=u'MY NAME',
    address=AddressList([
        Address(
            address_type=u'Work',
            line1=u'My Office',
            line2=u'Big Office Block',
            city=u'Mega City',
            country=u'The Old Sod'
        ),
        Address(
            address_type=u'Home',
            line1=u'Home Sweet Home',
            line2=u'Easy Street',
            city=u'Burbs',
            country=u'The Old Sod'
        )
    ])
)


@adapter(AddressListField, IDataGridField)
@implementer(IDataConverter)
class GridDataConverter(BaseDataConverter):
    """Convert between the AddressList object and the widget.
       If you are using objects, you must provide a custom converter
    """

    def toWidgetValue(self, value):
        """Simply pass the data through with no change"""
        rv = list()
        for row in value:
            d = dict()
            for name, f in getFieldsInOrder(IAddress):
                d[name] = getattr(row, name)
            rv.append(d)
        return rv

    def toFieldValue(self, value):
        rv = AddressList()
        for row in value:
            d = dict()
            for name, f in getFieldsInOrder(IAddress):
                if row.get(name, NO_VALUE) != NO_VALUE:
                    d[name] = row.get(name)
            rv.append(Address(**d))
        return rv


# -------------[ Views Follow ]-------------------------------------------

class EditForm(form.EditForm):
    label = u'Simple Form (Objects)'

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
            setattr(context, k, v)

    def updateActions(self):
        """Bypass the baseclass editform - it causes problems"""
        super(form.EditForm, self).updateActions()

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['address'].allow_reorder = True


class EditForm2(EditForm):
    label = u'Hide the Row Manipulators (Objects)'
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm2, self).updateWidgets()
        self.widgets['address'].allow_insert = False
        self.widgets['address'].allow_delete = False


class EditForm3(EditForm):
    label = u'Disable Auto-append (Objects)'
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm3, self).updateWidgets()
        self.widgets['address'].auto_append = False


class EditForm4(EditForm):
    label = u'Omit a column - Column is Mandatory (Objects)'
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm4, self).updateWidgets()
        self.widgets['address'].columns = [
            c for c in self.widgets['address'].columns
            if c['name'] != 'country'
        ]

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('country')


class EditForm4b(EditForm):
    label = u'Omit a column - Column is Optional (Objects)'
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm4b, self).updateWidgets()
        self.widgets['address'].columns = [
            c for c in self.widgets['address'].columns
            if c['name'] != 'line2'
        ]

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('line2')


class EditForm5(EditForm):
    label = u'Configure Subform Widgets (Objects)'

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['line1'].size = 40
        widgets['line2'].size = 40
        widgets['city'].size = 20
        widgets['country'].size = 10


class EditForm6(EditForm):
    label = u'Hide a Column (Objects)'

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets['city'].mode = HIDDEN_MODE

    def updateWidgets(self):
        # This one hides the column title
        super(EditForm6, self).updateWidgets()
        self.widgets['address'].columns[3]['mode'] = HIDDEN_MODE


class EditForm7(EditForm):
    label = u'Table is read-only, cells editable (Objects)'

    def updateWidgets(self):
        super(EditForm7, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE


class EditForm8(EditForm):
    label = u'Table and cells are read-only (Objects)'

    def updateWidgets(self):
        super(EditForm8, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE
        for row in self.widgets['address'].widgets:
            for widget in row.subform.widgets.values():
                widget.mode = DISPLAY_MODE
