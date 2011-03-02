Introduction
============

Licence: GNU General Public License

This module provides a z3c.form version of the Products.DataGridField. This product
was developed for use with Plone4 and Dexterity.

Requirements
------------

    * Plone 4
    * z3c.forms
    * A browser with javascript support
    * jquery 1.4.3 or later

Installation
------------

Add collective.z3cform.datagridfield to your buildout eggs.::

    eggs=\
        ...
        collective.z3cform.datagridfield

Example usage
-------------

This piece of code demonstrates a schema which has a table within it.
The layout of the table is defined by a second schema.::

    from zope import schema
    from zope import interface
    from plone.directives import form
    
    from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
    
    class ITableRowSchema(interface.Interface):
        one = schema.TextLine(title=u"One")
        two = schema.TextLine(title=u"Two")
        three = schema.TextLine(title=u"Three")
    
    class IFormSchema(interface.Interface):
        four = schema.TextLine(title=u"Four")
        table = schema.List(title=u"Table"
            value_type=DictRow(title=u"tablerow", schema=ITableRowSchema))
    
    class EditForm(form.EditForm):
        extends(form.EditForm)
    
        grok.context(IFormSchema)
        grok.require('zope2.View')
        fields = field.Fields(IFormSchema)
        label=u"Demo Usage of DataGridField"
                
        fields['table'].widgetFactory = DataGridFieldFactory

Storage
-------

The data can be stored as either a list of dicts or a list of objects.
If the data is a list of dicts, the value_type is DictRow.
Otherwise, the value_type is 'schema.Object'. 

If you are providing an Object content type (as opposed to dicts) you
must provide your own conversion class. The default conversion class
returns a list of dicts, not of your object class. See the demos.

Configuration
-------------

The widget can be customised via the updateWidgets method.

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['table'].allow_insert = False # Enable/Disable the insert button on the right
        self.widgets['table'].allow_delete = False # Enable/Disable the delete button on the right
        self.widgets['table'].auto_append = False  # Enable/Disable the auto-append feature
        self.widgets['table'].allow_reorder = False  # Enable/Disable the re-order rows feature

The widget contains an attribute 'columns' which is manipulated to hide column
titles.

Manipulating the Sub-form
-------------------------

The DataGridField makes use of a subform to build each line. The main DataGridField
contains a DataGridFieldObject for each line in the table. The DataGridFieldObject
in turn creates the DataGridFieldObjectSubForm to store the fields.

There are two callbacks to your main form:

    datagridInitialise(subform, widget)
    
    *   This is called when the subform fields have been initialised, but before
        the widgets have been created. Field based configuration could occur here.

    datagridUpdateWidgets(subform, widgets, widget)

    *   This is called when the subform widgets have been created. At this point,
        you can configure the widgets, e.g. specify the size of a widget.

Notes
-----

I have attempted to keep the markup close to Products.DataGridField, so that the
styling approach is the same.

TODO
----

    * Testing

    * The mechanism to hide/omit columns is cumbersome. This needs to be revisited.

    * Better styling of table in read-only mode.
      Merge the display and input versions of the layout.

    * kss validation - highlight the incorrect row, rather than the entire widget.
      Possibly show the error message in the field cell.

    * hidden mode

Demo
----

Examples are in the package collective.z3cform.datagridfield_demo.

References
----------
 
    * http://pypi.python.org/pypi/Products.DataGridField
    * http://pypi.python.org/pypi/collective.z3cform.datagridfield_demo


