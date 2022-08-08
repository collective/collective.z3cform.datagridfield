Introduction
============

Provides a field with a datagrid (table), where each row is a sub form.

It is a `z3c.form <https://z3cform.readthedocs.io/en/latest/>`_ implementation of the `Products.DataGridField <http://plone.org/products/datagridfield>`_ .

This product was developed for use with Plone and Dexterity.

.. image:: https://github.com/collective/collective.z3cform.datagridfield/actions/workflows/test.yml/badge.svg
   :target: https://github.com/collective/collective.z3cform.datagridfield/actions/workflows/test.yml


Installation
============

Add collective.z3cform.datagridfield to your buildout eggs:

.. code-block:: ini

    [buildout]
    ...
    eggs =
        collective.z3cform.datagridfield


Example usage
=============

This piece of code demonstrates a schema which has a table within it.
The layout of the table is defined by a second schema:

.. code-block:: python

    from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
    from collective.z3cform.datagridfield.row import DictRow
    from plone.autoform.directives import widget
    from plone.autoform.form import AutoExtensibleForm
    from z3c.form import form
    from zope import interface
    from zope import schema


    class ITableRowSchema(interface.Interface):
        one = schema.TextLine(title=u"One")
        two = schema.TextLine(title=u"Two")
        three = schema.TextLine(title=u"Three")


    class IFormSchema(interface.Interface):
        four = schema.TextLine(title=u"Four")
        table = schema.List(
            title=u"Table",
            value_type=DictRow(
                title=u"tablerow",
                schema=ITableRowSchema,
            ),
        )

        widget(table=DataGridFieldFactory)


    class EditForm(AutoExtensibleForm, form.EditForm):
        label=u"Demo Usage of DataGridField"
        schema = IFormSchema


And configured via zcml:

.. code-block:: xml

    <browser:page
        name="editform--example"
        class=".editform.EditForm"
        for="*"
        permission="zope2.View"
        />


Also it can be used from a supermodel XML:

.. code-block:: xml

    <field name="table" type="zope.schema.List">
      <description/>
      <title>Table</title>
      <value_type type="collective.z3cform.datagridfield.DictRow">
        <schema>your.package.interfaces.ITableRowSchema</schema>
      </value_type>
      <form:widget type="collective.z3cform.datagridfield.DataGridFieldFactory"/>
    </field>


Storage
-------

The data can be stored as either a list of dicts or a list of objects.
If the data is a list of dicts, the value_type is DictRow.
Otherwise, the value_type is 'schema.Object'.

If you are providing an Object content type (as opposed to dicts) you must provide your own conversion class.
The default conversion class returns a list of dicts,
not of your object class.
See the demos.


Configuration
=============


Row editor handles
------------------

Widget parameters can be passed via widget hints. Extended schema example from above:

.. code-block:: python

    class IFormSchema(interface.Interface):
        four = schema.TextLine(title=u"Four")
        table = schema.List(
            title=u"Table",
            value_type=DictRow(
                title=u"tablerow",
                schema=ITableRowSchema,
            ),
        )

        widget(
            "table",
            DataGridFieldFactory,
            allow_insert=False,
            allow_delete=False,
            allow_reorder=False,
            auto_append=False,
            display_table_css_class="table table-striped",
            input_table_css_class="table table-sm",
        )



Manipulating the Sub-form
-------------------------

The `DictRow` schema can also be extended via widget hints. Extended schema examples from above:

.. code-block:: python

    from z3c.form.browser.checkbox import CheckBoxFieldWidget


    class ITableRowSchema(interface.Interface):

        two = schema.TextLine(title=u"Level 2")

        address_type = schema.Choice(
            title="Address Type",
            required=True,
            values=["Work", "Home"],
        )
        # show checkboxes instead of selectbox
        widget(address_type=CheckBoxFieldWidget)


    class IFormSchema(interface.Interface):

        table = schema.List(
            title=u"Nested selection tree test",
            value_type=DictRow(
                title=u"tablerow",
                schema=ITableRowSchema
            )
        )
        widget(table=DataGridFieldFactory)


Working with plone.app.registry
-------------------------------

To use the field with plone.app.registry, you'll have to use
a version of the field that has PersistentField as it's base
class:

.. code-block:: python

    from collective.z3cform.datagridfield.registry import DictRow


JavaScript events
-----------------

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

Example usage:

.. code-block:: javascript

    var handleDGFInsert = function(event, dgf, row) {
        row = $(row);
        console.log("Got new row:");
        console.log(row);
    };

    // Bind all DGF handlers on the page
    $(document).on('beforeaddrow beforeaddrowauto', '.datagridwidget-table-view', handleDGFInsert);


Demo
====

More examples are in the demo subfolder of this package.


Versions
========

* Version 3.x is Plone 6+ only (z3c.form >= 4)
* Versions 1.4.x and 2.x are for Plone 5.x,
* Versions 1.3.x is for Plone 4.3
* For Python 3.7 at least PyYAML 4.2b1


Requirements
============

* z3c.forms
* A browser with javascript support
* jquery 1.4.3 or later

