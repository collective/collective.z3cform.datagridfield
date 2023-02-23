from collective.z3cform.datagridfield.interfaces import IRow
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFields


@implementer(IFieldDeserializer)
@adapter(IRow, IDexterityContent, IBrowserRequest)
class DatagridRowDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        row_data = {}

        for name, field in getFields(self.field.schema).items():
            if field.readonly:
                continue

            deserializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldDeserializer
            )
            if deserializer is None:
                continue

            row_data[name] = deserializer(value[name])

        return row_data
