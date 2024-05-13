# from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
# from collective.z3cform.datagridfield.demo.interfaces import ITableRow
# from collective.z3cform.datagridfield.row import DictRow
# from plone import schema
# from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer


class IDGFTest(model.Schema):
    """Marker interface and Dexterity Python Schema for DGFTest"""

    # You can define the fields in the schema interface directly or load an XML
    # file ... see below
    # tabular_field = schema.List(
    #     title="datagridfield",
    #     value_type=DictRow(schema=ITableRow),
    #     required=False,
    # )
    # directives.widget(
    #     "tabular_field",
    #     DataGridFieldWidgetFactory,
    #     auto_append=True,
    #     allow_reorder=True,
    # )

    model.load("dgftest.xml")


@implementer(IDGFTest)
class DGFTest(Item):
    """Content-type class for IDGFTest"""
