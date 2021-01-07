# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield.row import DictRow
from transmogrify.dexterity.converters import DefaultSerializer
from transmogrify.dexterity.interfaces import ISerializer
from zope.component import adapter
from zope.interface import implementer
from zope.schema import getFields


@adapter(DictRow)
@implementer(ISerializer)
class DictRowSerializer:
    """Serializer to allow transmogrify.dexterity to write the dict. A custom
    deserializer doesn't seem to be necessary.
    """

    def __init__(self, field):
        self.field = field

    def _serializer(self, field_type):
        if field_type is not None:
                return ISerializer(field_type)
        return DefaultSerializer()

    def __call__(self, value, filestore, extra=None):
        """Create a new dict with all the contents serialized"""
        rv = {}
        for field_name, field_type in getFields(self.field.schema).items():
            rv[field_name] = self._serializer(
                field_type
            )(
                value.get(field_name),
                filestore,
                field_name
            )
        return rv
