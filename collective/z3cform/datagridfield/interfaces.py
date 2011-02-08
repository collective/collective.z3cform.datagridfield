
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ValidationError
from z3c.form.interfaces import IMultiWidget

class IDataGridField(IMultiWidget):
    """Grid widget."""

class AttributeNotFoundError(ValidationError):
    """An attribute is missing from the class"""

    def __init__(self, fieldname, schema):
        self.fieldname = fieldname
        self.schema = schema
        self.__doc__ = u'Missing Field %s required by schema %s' % (fieldname, schema)



class IRow(IObject):
    """A row. The schema defines dict keys.
    """

