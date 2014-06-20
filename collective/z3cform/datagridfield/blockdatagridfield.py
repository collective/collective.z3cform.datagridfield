import zope.interface
import zope.component
import zope.schema.interfaces
from zope.schema.interfaces import IObject

from z3c.form import interfaces
from z3c.form.widget import FieldWidget

from .datagridfield import DataGridField
from .datagridfield import DataGridFieldObject


class BlockDataGridField(DataGridField):
    """
    Render edit mode widgets in blocks (vertical) instead of cells (horizontal).
    """

    klass = "blockdatagridfield"

    def createObjectWidget(self, idx):
        """
        """
        valueType = self.field.value_type

        if IObject.providedBy(valueType):
            widget = BlockDataGridFieldObjectFactory(valueType, self.request)
            if idx in ['TT', 'AA']:
                widget.setErrors = False
            else:
                widget.setErrors = True
        else:
            widget = zope.component.getMultiAdapter((valueType, self.request), interfaces.IFieldWidget)

        return widget


class BlockDataGridFieldObject(DataGridFieldObject):
    """
    Define one row as a widget in BDGF.

    Does not override functionality, but exist to allow template overriding.
    """


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def BlockDataGridFieldFactory(field, request):
    """IFieldWidget factory for BlockDataGridField."""
    return FieldWidget(field, BlockDataGridField(request))


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def BlockDataGridFieldObjectFactory(field, request):
    """IFieldWidget factory for DataGridField."""

    # Create a normal DataGridFieldObject widget
    widget = FieldWidget(field, BlockDataGridFieldObject(request))
    return widget
