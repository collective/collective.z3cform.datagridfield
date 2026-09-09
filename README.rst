Introduction
============

Provides a field with a datagrid (table), where each row is a sub form.

It is a `z3c.form <https://z3cform.readthedocs.io/en/latest/>`_ implementation of the `Products.DataGridField <https://github.com/collective/Products.DataGridField>`_.

This product was developed for use with Plone and Dexterity.

.. image:: https://github.com/collective/collective.z3cform.datagridfield/actions/workflows/test-matrix.yml/badge.svg
   :target: https://github.com/collective/collective.z3cform.datagridfield/actions/workflows/test-matrix.yml


Installation
============

Install it with pip:

.. code-block:: shell

    pip install collective.z3cform.datagridfield

Or add it to your buildout eggs:

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
        one = schema.TextLine(title="One")
        two = schema.TextLine(title="Two")
        three = schema.TextLine(title="Three")


    class IFormSchema(interface.Interface):
        four = schema.TextLine(title="Four")
        table = schema.List(
            title="Table",
            value_type=DictRow(
                title="tablerow",
                schema=ITableRowSchema,
            ),
        )

        widget(table=DataGridFieldFactory)


    class EditForm(AutoExtensibleForm, form.EditForm):
        label="Demo Usage of DataGridField"
        schema = IFormSchema


And configured via zcml:

.. code-block:: xml

    <browser:page
        name="editform--example"
        class=".editform.EditForm"
        for="*"
        permission="zope2.View"
        />


Besides ``DataGridFieldFactory`` there is ``BlockDataGridFieldFactory``
(``collective.z3cform.datagridfield.blockdatagridfield``), which renders every
cell as a block below each other instead of a table row.
Both are aliases for ``DataGridFieldWidgetFactory`` and
``BlockDataGridFieldWidgetFactory``.

Also it can be used from a supermodel XML:

.. code-block:: xml

    <field name="table" type="zope.schema.List">
      <description/>
      <title>Table</title>
      <value_type type="collective.z3cform.datagridfield.row.DictRow">
        <schema>your.package.interfaces.ITableRowSchema</schema>
      </value_type>
      <form:widget type="collective.z3cform.datagridfield.datagridfield.DataGridFieldFactory"/>
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
        four = schema.TextLine(title="Four")
        table = schema.List(
            title="Table",
            value_type=DictRow(
                title="tablerow",
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

        two = schema.TextLine(title="Level 2")

        address_type = schema.Choice(
            title="Address Type",
            required=True,
            values=["Work", "Home"],
        )
        # show checkboxes instead of selectbox
        widget(address_type=CheckBoxFieldWidget)


    class IFormSchema(interface.Interface):

        table = schema.List(
            title="Nested selection tree test",
            value_type=DictRow(
                title="tablerow",
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

``collective.z3cform.datagridfield`` fires events on the widget element
``div.pat-datagridfield``, so that you can hook them in your own JavaScript
for DataGridField behavior customization.

Native DOM events (dispatched via ``dispatchEvent``, no extra arguments):

* ``afterdatagridfieldinit`` - the DataGridField has been initialized.
  This is the only event that bubbles.

* ``beforeaddrowauto`` / ``afteraddrowauto`` - before/after a row is
  auto-appended while editing the last row.

jQuery events (triggered via ``$el.trigger``, with arguments):

* ``beforeaddrow`` / ``afteraddrow`` [$datagridfield, $newRow]

* ``aftermoverow`` [$datagridfield, row]

Example usage:

.. code-block:: javascript

    // native DOM event
    document.addEventListener("afterdatagridfieldinit", function (event) {
        console.log("DataGridField initialized:", event.target);
    });

    // jQuery events
    $(document).on("beforeaddrow afteraddrow", ".pat-datagridfield", function (event, $dgf, $row) {
        console.log("Got new row:", $row);
    });


Demo
====

More examples are in the demo subfolder of this package.


Versions
========

* Version 4.x is for Plone 6.2 and Python 3.10+ (PEP 420 namespace package)
* Version 3.x is for Plone 6.0 and 6.1 (z3c.form >= 4)
* Versions 1.4.x and 2.x are for Plone 5.x
* Version 1.3.x is for Plone 4.3


Requirements
============

* z3c.form
* A browser with JavaScript support

