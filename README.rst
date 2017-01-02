Introduction
============

This module provides a z3c.form version of the `Products.DataGridField <http://plone.org/products/datagridfield>`_ . This product
was developed for use with Plone4/5 and Dexterity.

.. image:: https://travis-ci.org/collective/collective.z3cform.datagridfield.png
   :target: http://travis-ci.org/collective/collective.z3cform.datagridfield

.. contents :: :local:


Requirements
============

* Plone 4 or Plone 5
* z3c.forms
* A browser with javascript support
* jquery 1.4.3 or later


Installation
============

Add collective.z3cform.datagridfield to your buildout eggs.::

    eggs=\
        ...
        collective.z3cform.datagridfield


Example usage
=============

This piece of code demonstrates a schema which has a table within it.
The layout of the table is defined by a second schema.::

    from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

    from plone.supermodel import model
    from plone.autoform.form import AutoExtensibleForm

    from zope import schema
    from z3c.form import field, button, form


    class ITableRowSchema(model.Schema):
        one = schema.TextLine(title=u"One")
        two = schema.TextLine(title=u"Two")
        three = schema.TextLine(title=u"Three")


    class IFormSchema(model.Schema):
        four = schema.TextLine(title=u"Four")

        table = schema.List(
                title=u"Table",
                default=[],
                value_type=DictRow(
                        title=u"Rows",
                        schema=ITableRowSchema,
                    ),
                required=False,
            )


    class MyForm(AutoExtensibleForm, form.Form):
        """ Define Form handling

        This form can be accessed as http://yoursite/@@my-form

        """
        schema = IFormSchema
        ignoreContext = True

        fields = field.Fields(IFormSchema)
        fields['table'].widgetFactory = DataGridFieldFactory

        label = u"Example"
        description = u"Simple, sample form"

        @button.buttonAndHandler(u'Ok')
        def handleApply(self, action):
            data, errors = self.extractData()
            if errors:
                self.status = self.formErrorsMessage
                return

            # Do something with valid data here

            # Set status on this form page
            # (this status message is not bind to the session and does not go thru redirects)
            self.status = "Thank you very much!"

        @button.buttonAndHandler(u"Cancel")
        def handleCancel(self, action):
            """User cancelled. Redirect back to the front page.
            """

Also it can be used from a supermodel xml::

    <field name="table" type="zope.schema.List">
      <description/>
      <title>Table</title>
      <value_type type="collective.z3cform.datagridfield.DictRow">
        <schema>your.package.interfaces.ITableRowSchema</schema>
      </value_type>
      <form:widget type="collective.z3cform.datagridfield.DataGridFieldFactory"/>
    </field>


Storage
=======

The data can be stored as either a list of dicts or a list of objects.
If the data is a list of dicts, the value_type is DictRow.
Otherwise, the value_type is 'schema.Object'.

If you are providing an Object content type (as opposed to dicts) you
must provide your own conversion class. The default conversion class
returns a list of dicts, not of your object class. See the demos.


Configuration
=============


Row editor handles
------------------

The widget can be customised via the updateWidgets method.

::

    def updateWidgets(self):
        super(MyForm, self).updateWidgets()
        self.widgets['table'].allow_insert = False # Enable/Disable the insert button on the right
        self.widgets['table'].allow_delete = False # Enable/Disable the delete button on the right
        self.widgets['table'].auto_append = False  # Enable/Disable the auto-append feature
        self.widgets['table'].allow_reorder = False  # Enable/Disable the re-order rows feature
        self.widgets['table'].main_table_css_class = 'my_custom_class'  # Change the class applied on the main table when the field is displayed

The widget contains an attribute 'columns' which is manipulated to hide column
titles.


Block edit mode
===============

A widget class variation ``BlockDataGridField`` is provided.
This widget renders subform widgets vertically in blocks instead
of horizontally in cells. It makes sense when there are many
subform fields and they have problem to fit on the screen once.

Example::

    class EditForm9(EditForm):
        label = u'Rendering widgets as blocks instead of cells'

        ...

        def update(self):
            # Set a custom widget for a field for this form instance only
            self.fields['address'].widgetFactory = BlockDataGridFieldFactory
            super(EditForm9, self).update()


Manipulating the Sub-form
=========================

The DataGridField makes use of a subform to build each line. The main DataGridField
contains a DataGridFieldObject for each line in the table. The DataGridFieldObject
in turn creates the DataGridFieldObjectSubForm to store the fields.

There are two callbacks to your main form:

**datagridInitialise(subform, widget)**

* This is called when the subform fields have been initialised, but before
  the widgets have been created. Field based configuration could occur here.

**datagridUpdateWidgets(subform, widgets, widget)**

* This is called when the subform widgets have been created. At this point,
  you can configure the widgets, e.g. specify the size of a widget.

Here is an example how one can customize per-field widgets for the data grid field::

    from zope import schema
    from zope import interface
    from Products.CMFCore.interfaces import ISiteRoot

    from plone.autoform import directives as form

    from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
    from .widget import DGFTreeSelectFieldWidget


    class ITableRowSchema(form.Schema):

        form.widget('one', DGFTreeSelectFieldWidget)
        one = schema.TextLine(title=u"Level 1")

        form.widget('two', DGFTreeSelectFieldWidget)
        two = schema.TextLine(title=u"Level 2")

        # Uses the default widget
        three = schema.TextLine(title=u"Level 3")


    class IFormSchema(form.Schema):

        form.widget(table=DataGridFieldFactory)
        table = schema.List(title=u"Nested selection tree test",
            value_type=DictRow(title=u"tablerow", schema=ITableRowSchema))


Working with plone.app.registry
===============================

To use the field with plone.app.registry, you'll have to use
a version of the field that has PersistentField as it's base
class::

    from collective.z3cform.datagridfield.registry import DictRow


Javascript events
=================

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

    var handleDGFInsert = function(event, dgf, row) {
        row = $(row);
        console.log("Got new row:");
        console.log(row);
    };

    // Bind all DGF handlers on the page
    $(document).on('beforeaddrow beforeaddrowauto', '.datagridwidget-table-view', handleDGFInsert);


Demo
====

Examples are in the package `collective.z3cform.datagridfield_demo <https://github.com/collective/collective.z3cform.datagridfield_demo>`_.


See also
========

* https://github.com/collective/collective.z3cform.dgftreeselect

* https://github.com/collective/collective.z3cform.widgets/


References
==========

* http://pypi.python.org/pypi/Products.DataGridField

* http://pypi.python.org/pypi/collective.z3cform.datagridfield_demo
