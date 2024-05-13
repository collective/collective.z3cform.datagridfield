from plone import schema
from plone.app.z3cform.widgets.select import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import Interface
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
