# -*- coding: utf-8 -*-
"""
    Code an concept courtesy of Martin Aspeli
"""
from interfaces import AttributeNotFoundError
from interfaces import IRow
from interfaces import IRowList
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IDataManager
from z3c.form.datamanager import AttributeField
from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.schema import Field
from zope.schema import getFields
from zope.schema import Object
from zope.schema import List
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import WrongContainedType


@implementer(IRow)
class DictRow(Object):
    __doc__ = IRow.__doc__
    _type = dict

    def __init__(self, schema, **kw):
        super(DictRow, self).__init__(schema, **kw)

    def _validate(self, value):
        # XXX HACK: Can't call the super, since it'll check to
        # XXX see if we provide DictRow.
        # We're only a dict, so we can't.
        # super(DictRow, self)._validate(value)

        # Validate the dict against the schema
        # Pass 1 - ensure fields are present
        if value is NO_VALUE:
            return
        # Treat readonly fields
        for field_name in getFields(self.schema).keys():
            field = self.schema[field_name]
            if field.readonly:
                value[field_name] = field.default
        errors = []
        for field_name in getFields(self.schema).keys():
            if field_name not in value:
                errors.append(AttributeNotFoundError(field_name, self.schema))

        if errors:
            raise WrongContainedType(errors, self.__name__)

        # Pass 2 - Ensure fields are valid
        for field_name, field_type in getFields(self.schema).items():
            if IChoice.providedBy(field_type):
                # Choice must be bound before validation otherwise
                # IContextSourceBinder is not iterable in validation
                bound = field_type.bind(value)
                bound.validate(value[field_name])
            else:
                field_type.validate(value[field_name])

    def set(self, object, value):
        # Override Object field logic
        Field.set(self, object, value)


@implementer(IRowList)
class RowList(List):
    __doc__ = IRowList.__doc__


@adapter(Interface, IRowList)
class RowDataManager(AttributeField):
    """Proxy to call datamanager for each field in the subform."""

    @property
    def subfields(self):
        return getFields(self.field.value_type.schema)

    def get(self):
        """Gets the target"""
        raw_value = []
        # Calling query() here will lead to infinite recursion!
        try:
            raw_value = super(RowDataManager, self).get()
        except AttributeError:
            raw_value = None
        if not raw_value:
            return []

        resolved_value = []
        for item in raw_value:
            new_item = {}
            for name, field in self.subfields.items():
                dm = getMultiAdapter((item, field), IDataManager)
                new_item[name] = dm.get()
            resolved_value.append(new_item)
        return resolved_value

    def set(self, value):
        """Sets the relationship target"""
        value = value or []
        new_value = []
        for item in value:
            new_item = {}
            for name, field in self.subfields.items():
                dm = getMultiAdapter((new_item, field), IDataManager)
                dm.set(item[name])
            new_value.append(new_item)
        super(RowDataManager, self).set(new_value)
