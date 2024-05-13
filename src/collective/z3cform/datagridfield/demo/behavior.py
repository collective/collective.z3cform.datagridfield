from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.app.z3cform.widgets.select import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.schema.vocabulary import SimpleVocabulary


class ITableRow(Interface):
    col1 = schema.TextLine(title="Column1")
    col2 = schema.Choice(
        vocabulary=SimpleVocabulary.fromValues(["yes", "no"]), required=False
    )
    links = RelationList(
        title="Related Links",
        value_type=RelationChoice(
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )

    tags = schema.Tuple(
        title="Tags",
        value_type=schema.TextLine(),
        required=False,
    )

    directives.widget(
        "tags",
        AjaxSelectFieldWidget,
        vocabulary="plone.app.vocabularies.Keywords",
    )

    image = namedfile.NamedBlobImage(
        title="Image",
        required=False,
    )


@provider(IFormFieldProvider)
class IDatagridfieldMetadata(model.Schema):

    tabular_field = schema.List(
        title="datagridfield",
        value_type=DictRow(schema=ITableRow),
        required=False,
    )
    directives.widget(
        "tabular_field",
        DataGridFieldWidgetFactory,
        auto_append=True,
        allow_reorder=True,
    )
