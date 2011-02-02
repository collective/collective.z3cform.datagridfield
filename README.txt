Introduction
============

Licence: GNU General Public License

I want to provide a z3c.form version of the Products.DataGridField. This product
was developed for use with Plone4 and Dexterity.

Requirements

Plone 4
z3c.forms
A browser with javascript support
jquery 1.4.3 or later

Installation

Add collective.z3cforms.datagridfield to your buildout eggs.

Example usage

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

    widget.allow_insert =  Enable the insert button on the right
    widget.allow_delete = Enable the delete button on the right
    widget.auto_append = Enable the auto-append feature

Notes

I have attempted to keep the markup close to Products.DataGridField, so that the
styling approach is the same.

If you are passing through a list of objects, you need to implement the dictionary
interface.

    def get(self, name, default=None):
        return getattr(self, name, default)
    
    def set(self, name, value):
        return setattr(self, name, value)


TODO

I convert the return value to a list of dictionaries. It should be a list of objects
of the correct type. The data transformations need to be looked at again.

Testing

References
 
http://pypi.python.org/pypi/Products.DataGridField


