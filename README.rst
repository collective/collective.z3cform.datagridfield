Introduction
==================

This module provides a z3c.form version of the `Products.DataGridField <http://plone.org/products/datagridfield>`_ . This product
was developed for use with Plone4 and Dexterity.

.. image:: https://travis-ci.org/collective/collective.z3cform.datagridfield.png
   :target: http://travis-ci.org/collective/collective.z3cform.datagridfield

.. contents :: :local:

Requirements
==================

    * Plone 4
    * z3c.forms
    * A browser with javascript support
    * jquery 1.4.3 or later

Installation
==================

Add collective.z3cform.datagridfield to your buildout eggs.::

    eggs=\
        ...
        collective.z3cform.datagridfield

Example usage
==================

This piece of code demonstrates a schema which has a table within it.
The layout of the table is defined by a second schema.::

    from zope import schema
    from zope import interface
    from plone.directives import form
    from z3c.form.form import extends
    from z3c.form import field

    from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

    class ITableRowSchema(interface.Interface):
        one = schema.TextLine(title=u"One")
        two = schema.TextLine(title=u"Two")
        three = schema.TextLine(title=u"Three")

    class IFormSchema(interface.Interface):
        four = schema.TextLine(title=u"Four")
        table = schema.List(title=u"Table",
            value_type=DictRow(title=u"tablerow", schema=ITableRowSchema))

    class EditForm(form.EditForm):
        extends(form.EditForm)

        grok.context(IFormSchema)
        grok.require('zope2.View')
        fields = field.Fields(IFormSchema)
        label=u"Demo Usage of DataGridField"

        fields['table'].widgetFactory = DataGridFieldFactory

You can also use grok'ed forms where you subclass the schema
from ``plone.directives.form.SchemaForm`` and declare
widgets witin the schema using ``form.widget()``.

Storage
==================

The data can be stored as either a list of dicts or a list of objects.
If the data is a list of dicts, the value_type is DictRow.
Otherwise, the value_type is 'schema.Object'.

If you are providing an Object content type (as opposed to dicts) you
must provide your own conversion class. The default conversion class
returns a list of dicts, not of your object class. See the demos.

Configuration
==================

Row editor handles
---------------------

The widget can be customised via the updateWidgets method.

::

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['table'].allow_insert = False # Enable/Disable the insert button on the right
        self.widgets['table'].allow_delete = False # Enable/Disable the delete button on the right
        self.widgets['table'].auto_append = False  # Enable/Disable the auto-append feature
        self.widgets['table'].allow_reorder = False  # Enable/Disable the re-order rows feature
        self.widgets['table'].main_table_css_class = 'my_custom_class'  # Change the class applied on the main table when the field is displayed

The widget contains an attribute 'columns' which is manipulated to hide column
titles.

Block edit mode
====================================

A widget class variation ``BlockDataGridField`` is provided.
This widget renders subform widgets vertically in blocks instead
of horizontally in cells. It makes sense when there are many
subform fields and they have problem to fit on the screen once.

Example::

    class EditForm9(EditForm):
        label = u'Rendering widgets as blocks instead of cells'

        grok.name('demo-collective.z3cform.datagrid-block-edit')

        def update(self):
            # Set a custom widget for a field for this form instance only
            self.fields['address'].widgetFactory = BlockDataGridFieldFactory
            super(EditForm9, self).update()

Manipulating the Sub-form
====================================

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

Here is an example how one can customize per-field widgets for the data grid field::

    from zope import schema
    from zope import interface
    from Products.CMFCore.interfaces import ISiteRoot

    from five import grok

    from plone.directives import form

    from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
    from .widget import DGFTreeSelectFieldWidget


    class ITableRowSchema(form.Schema):

        form.widget(one=DGFTreeSelectFieldWidget)
        one = schema.TextLine(title=u"Level 1")

        form.widget(two=DGFTreeSelectFieldWidget)
        two = schema.TextLine(title=u"Level 2")

        # Uses the default widget
        three = schema.TextLine(title=u"Level 3")


    class IFormSchema(form.Schema):

        form.widget(table=DataGridFieldFactory)
        table = schema.List(title=u"Nested selection tree test",
            value_type=DictRow(title=u"tablerow", schema=ITableRowSchema))


Working with plone.app.registry
====================================

To use the field with plone.app.registry, you'll have to use
a version of the field that has PersistentField as it's base
class::

    from collective.z3cform.datagridfield.registry import DictRow

Javascript events
====================================

``collective.z3cform.datagridfield`` fires jQuery events,
so that you can hook them in your own Javascript for DataGridField
behavior customization.

The following events are currently fired against ``table.datagridwidget-table-view``

* ``beforeaddrow`` [datagridfield, newRow]

* ``afteraddrow`` [datagridfield, newRow]

* ``beforeaddrowauto`` [datagridfield, newRow]

* ``afteraddrowauto`` [datagridfield, newRow]

* ``aftermoverow`` [datagridfield]

* ``afterdatagridfieldinit`` - All DGFs on the page have been initialized

Example usage::

    handleDGFInsert : function(event, dgf, row) {
        row = $(row);
        console.log("Got new row:");
        console.log(row);
    },

    // Bind all DGF handlers on the page
    $(document.body).delegate(".datagridwidget-table-view", "beforeaddrow beforeaddrowauto", handleDGFInsert);

Demo
====================================

Examples are in the package `collective.z3cform.datagridfield_demo <https://github.com/collective/collective.z3cform.datagridfield_demo>`_.

See also
====================================

* https://github.com/miohtama/collective.z3cform.dgftreeselect

* https://github.com/collective/collective.z3cform.widgets/

References
====================================

    * http://pypi.python.org/pypi/Products.DataGridField
    * http://pypi.python.org/pypi/collective.z3cform.datagridfield_demo
