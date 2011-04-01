"""
    Code an concept coutesy of Martin Aspeli
"""

from zope.interface import implements
from zope.schema.interfaces import WrongContainedType
from zope.schema import Object, Field
from zope.schema import getFields

from interfaces import IRow
from interfaces import AttributeNotFoundError

class DictRow(Object):
    __doc__ = IRow.__doc__
    implements(IRow)
    _type = dict

    def __init__(self, schema, **kw):
        super(DictRow, self).__init__(schema, **kw)

    def _validate(self, value):
        #HACK: Can't call the super, since it'll check to see if we provide DictRow.
        #We're only a dict, so we can't.
        # super(DictRow, self)._validate(value)

        # Validate the dict against the schema
        # Pass 1 - ensure fields are present
        errors = []
        for field_name in getFields(self.schema).keys():
            if field_name not in value:
                errors.append(AttributeNotFoundError(field_name, self.schema))

        if errors:
            raise WrongContainedType(errors, self.__name__)

        # Pass 2 - Ensure fields are valid
        for field_name, field_type in getFields(self.schema).items():
            field_type.validate(value[field_name])

    def set(self, object, value):
        # Override Object field logic
        Field.set(self, object, value)

