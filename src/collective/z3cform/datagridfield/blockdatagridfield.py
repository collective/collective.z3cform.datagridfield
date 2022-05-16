# -*- coding: utf-8 -*-
from .datagridfield import DataGridFieldObjectWidget
from .datagridfield import DataGridFieldWidget
from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from zope.schema.interfaces import IObject

import zope.component
import zope.interface
import zope.schema.interfaces


class BlockDataGridFieldWidget(DataGridFieldWidget):
    """
    Render edit mode widgets in blocks (vertical) instead of cells
    (horizontal).
    """

    klass = "blockdatagridfield"

    def createObjectWidget(self, idx):
        """"""
        valueType = self.field.value_type

        if IObject.providedBy(valueType):
            widget = BlockDataGridFieldObjectFactory(valueType, self.request)
            if idx in ["TT", "AA"]:
                widget.setErrors = False
            else:
                widget.setErrors = True
        else:
            widget = zope.component.getMultiAdapter(
                (valueType, self.request), interfaces.IFieldWidget
            )

        return widget


class BlockDataGridFieldObjectWidget(DataGridFieldObjectWidget):
    """
    Define one row as a widget in BDGF.

    Does not override functionality, but exist to allow template overriding.
    """


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def BlockDataGridFieldWidgetFactory(field, request):
    """IFieldWidget factory for BlockDataGridFieldWidget."""
    return FieldWidget(field, BlockDataGridFieldWidget(request))


# BBB
BlockDataGridFieldFactory = BlockDataGridFieldWidgetFactory


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def BlockDataGridFieldObjectWidgetFactory(field, request):
    """IFieldWidget factory for DataGridFieldWidget."""

    # Create a normal DataGridFieldObjectWidget widget
    widget = FieldWidget(field, BlockDataGridFieldObjectWidget(request))
    return widget


# BBB
BlockDataGridFieldObjectFactory = BlockDataGridFieldObjectWidgetFactory
