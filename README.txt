============
Introduction
============

Licence: GNU General Public License

I want to provide a z3c.form version of the Products.DataGridField. This product
was developed for use with Plone4 and Dexterity.

Requirements
------------

Plone 4
z3c.forms
A browser with javascript support
jquery 1.4.3 or later

Installation
------------

Add collective.z3cforms.datagridfield to your buildout eggs.

Example usage
-------------

from zope import schema
from zope import interface
from plone.directives import form

form collective.z3cforms.datagridfield import DataGridFieldFactory

class ITableRowSchema(interface.Interface):
    one = schema.TextLine(title=u"One")
    two = schema.TextLine(title=u"Two")
    three = schema.TextLine(title=u"Three")

class IFormSchema(interface.Interface):
    four = schema.TextLine(title=u"Four")
    table = schema.List(title=u"Table"
        value_type=schema.Object(title=u"tablerow", schema=ITableRowSchema))

class EditForm(form.EditForm):
    extends(form.EditForm)

    grok.context(IFormSchema)
    grok.require('zope2.View')
    fields = field.Fields(IFormSchema)
    label=u"Demo Usage of DataGridField"
            
    fields['table'].widgetFactory = DataGridFieldFactory

Configuration
-------------

Unfortunately, due to the way in which the widgets and sub-widgets are setup, it
is difficult to configure the widget after it is created. Instead, you create
a customised factory with the configuration that you need.


def CustomisedDataGridFieldFactory(field, request):
    widget = DataGridField(request)
    rv = FieldWidget(field, widget)
    widget.allow_insert = False   # Enable the insert button on the right
    widget.allow_delete = False   # Enable the delete button on the right
    widget.auto_append = False    # Enable the auto-append feature
    return rv

...
    fields['table'].widgetFactory = CustomDataGridFieldFactory

Manipulating the Sub-form
-------------------------

The DataGridField makes use of a subform to build each line. The main DataGridField
contains a DataGridFieldObject for each line in the table. The DataGridFieldObject
in turn creates the DataGridFieldObjectSubForm to store the fields.

There are two callbacks to your main form:

    datagridInitialise(subform, widget)
    
        This is called when the subform fields have been initialised, but before
        the widgets have been created. Field based configuration could occur here.

        Note: omiting fields causes an error. If you want to omit fields, create
        a separate schema instead.

    datagridUpdateWidgets(subform, widgets, widget)

        This is called when the subform widgets have been created. At this point,
        you can configure the widgets, e.g. specify the size of a widget.

Notes
-----

I have attempted to keep the markup close to Products.DataGridField, so that the
styling approach is the same.

If you are passing through a list of objects (as opposed to a list of dicts), you
need to implement the dictionary interface on the object.

    def get(self, name, default=None):
        return getattr(self, name, default)
    
    def set(self, name, value):
        return setattr(self, name, value)


TODO
----

I convert the return value to a list of dictionaries. It should be a list of objects
of the correct type. The data transformations need to be looked at again.

    Testing

References
----------
 
http://pypi.python.org/pypi/Products.DataGridField


