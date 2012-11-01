import zope.interface
import zope.component
import zope.schema.interfaces
from zope.schema.interfaces import IObject
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form import interfaces
from z3c.form.widget import FieldWidget

from .datagridfield import DataGridField
from .datagridfield import DataGridFieldObject


class BlockDataGridField(DataGridField):
    """
    Render edit mode widgets in blocks (vertical) instead of cells (horizontal).
    """

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
            widget = zope.component.getMultiAdapter((valueType, self.request),
                interfaces.IFieldWidget)

        return widget

    def getNormalRows(self):
        """
        Get all DGF rows filled on the postback or were already filled when editing started.
        """
        rows = []
        for w in self.widgets:
            if w.name.endswith("TT") or w.name.endswith("AA"):
                continue
            rows.append(w)
        return rows

    def getTTRows(self):
        """
        Insert template rows.
        """
        for w in self.widgets:
            if w.name.endswith("TT"):
                return [w]
        return []

    def getAARows(self):
        """
        Auto-append template rows.
        """
        for w in self.widgets:
            if w.name.endswith("AA"):
                return [w]
        return []


class BlockDataGridFieldObject(DataGridFieldObject):
    """
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
    widget = FieldWidget(field, DataGridFieldObject(request))
    # Then customize its template
    widget.template = ViewPageTemplateFile("datagridfieldobject_input_block.pt")
    return widget


