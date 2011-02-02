"""
    Implementation of the widget
"""


import zope.interface
import zope.schema.interfaces
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.schema import Object
from zope.schema.interfaces import IList
from z3c.form import button
from z3c.form.browser.object import ObjectWidget
from z3c.form.object import SubformAdapter, ObjectSubForm


from five import grok

from z3c.form.browser.multi import MultiWidget
from z3c.form import interfaces

from z3c.form.interfaces import IMultiWidget, IValidator
from z3c.form.widget import FieldWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.validator import SimpleFieldValidator


class IDataGridField(IMultiWidget):
    """Grid widget."""

class DataGridFieldHandler(grok.View):
    """Handler for Ajax Calls on this widget
        This is not used.
    """
    grok.context(IDataGridField)

    def __call__(self):

        print 'DataGridFieldHandler', self.request.form

    def render(self):
        pass

class DataGridField(MultiWidget):
    """This grid should be applied to an schema.List item which has
    schema.Object and an interface"""

    zope.interface.implements(IDataGridField)

    allow_insert = True
    allow_delete = True
    auto_append = True

    def setField(self, value):
        """
            The field information is passed to the widget after it is initialised.
            Use this call to initialise the column definitions.
        """
        self._field = value

        self.columns = []
        for name, field in getFieldsInOrder(self._field.value_type.schema):
            col = {
                'name': name,
                'field': field,
                'label': field.title,
                'required': field.required,
                'mode': None,
                'callback': None, 
                'widgetFactory': None,
            }
            self.columns.append(col)

    def getField(self):
        return self._field

    field = property(getField, setField)

    def select(self, *names):
        self.columns = [col for col in self.columns if col['name'] in names]

    def omit(self, *names):
        self.columns = [col for col in self.columns if col['name'] not in names]

##     def URL(self):
##         form_url = self.request.getURL()
## 
##         form_prefix = self.form.prefix + self.__parent__.prefix
##         widget_name = self.name[len(form_prefix):]
##         return "%s/++widget++%s/@@datagridfieldhandler" % (form_url, widget_name,)
## 

    def getWidget(self, idx):
        """Create the object widget. This is used to avoid looking up the widget"""
        valueType = self.field.value_type
        if type(valueType) == Object:
            widget = DataGridFieldObjectFactory(valueType, self.request)
        else:
            widget = zope.component.getMultiAdapter((valueType, self.request),
                interfaces.IFieldWidget)
        self.setName(widget, idx)

        widget.__parent__ = self

        widget.mode = self.mode
        widget.klass = 'row'
        #set widget.form (objectwidget needs this)
        if interfaces.IFormAware.providedBy(self):
            widget.form = self.form
            zope.interface.alsoProvides(
                widget, interfaces.IFormAware)
        widget.update()
        return widget

    def name_prefix(self):
        return self.prefix
    def id_prefix(self):
        return self.prefix.replace('.', '-')

    def updateWidgets(self):
        super(DataGridField, self).updateWidgets()
        if self.auto_append:
            # If we are doing 'auto-append', then a blank row needs to be added
            idx = len(self.widgets)
            widget = self.getWidget('AA')
            widget.klass = 'datagridwidget-row auto-append'
            self.widgets.append(widget)
            self.setName(widget, 'autoappend')

            # Set the handler
            #for w in widget.subform.widgets.values():
            #    w.onchange = u"dataGridField2Functions.autoInsertRow(this)"

        if self.auto_append or self.allow_insert:
            # If we can add rows, we need a template row
            idx = len(self.widgets)
            template = self.getWidget('TT')
            template.klass = 'datagridwidget-row datagridwidget-empty-row'
            self.widgets.append(template)

    def setName(self, widget, idx):
        """This version facilitates inserting non-numerics"""
        widget.name = '%s.%s' % (self.name, idx)
        widget.id = '%s-%s' % (self.id, idx)

    @property
    def counterMarker(self):
        # Override this to exclude template line and auto append line
        counter = len(self.widgets)
        if self.auto_append:
            counter -= 1
        if self.auto_append or self.allow_insert:
            counter -= 1
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counterName, counter)


@grok.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@grok.implementer(interfaces.IFieldWidget)
def DataGridFieldFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, DataGridField(request))

class GridDataConverter(grok.MultiAdapter, BaseDataConverter):
    """Convert between the context and the widget"""
    
    grok.adapts(zope.schema.interfaces.IList, IDataGridField)
    grok.implements(interfaces.IDataConverter)

    def toWidgetValue(self, value):
        """Simply pass the data through with no change"""
        return value

    def toFieldValue(self, value):
        return value


class DataGridFieldObject(ObjectWidget):

    def update(self):
        """I want to initialise widget data"""
        #very-very-nasty: skip raising exceptions in extract while we're updating
        self._updating = True
        try:
            super(ObjectWidget, self).update()

            # Now the sub-form has fields that can be customised - call form function
            # if one exists
            if hasattr(self.form, 'datagridInitialise'):
                self.form.datagridInitialise(self.subform, self.__parent__)
            self.updateWidgets(setErrors=False)
        finally:
            self._updating = False

    def isInsertEnabled(self):
        return self.__parent__.allow_insert

    def isDeleteEnabled(self):
        return self.__parent__.allow_delete

    def portal_url(self):
        return self.__parent__.context.portal_url()

@grok.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@grok.implementer(interfaces.IFieldWidget)
def DataGridFieldObjectFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, DataGridFieldObject(request))


class DataGridFieldObjectSubForm(ObjectSubForm):
    """Local class of subform - this is intended to all configuration information
    to be passed all the way down to the subform.
    """
    def updateWidgets(self):
        rv = super(DataGridFieldObjectSubForm, self).updateWidgets()
        if hasattr(self.__parent__.form, 'datagridUpdateWidgets'):
            self.__parent__.form.datagridUpdateWidgets(self, self.widgets, self.__parent__.__parent__)
        return rv



class DataGridFieldSubformAdapter(grok.MultiAdapter, SubformAdapter):
    """Give it my local class of subform, rather than the default"""

    grok.implements(interfaces.ISubformFactory)
    grok.adapts(zope.interface.Interface, #widget value
                          interfaces.IFormLayer,    #request
                          zope.interface.Interface, #widget context
                          zope.interface.Interface, #form
                          DataGridFieldObject,      #widget
                          zope.interface.Interface, #field
                          zope.interface.Interface) #field.schema

    factory = DataGridFieldObjectSubForm

class DataGridValidator(grok.MultiAdapter, SimpleFieldValidator):
    """
        I am crippling this validator - I return a list of dictionaries. If I don't
        cripple this it will fail because the return type is not of the correct object 
        type. For stronger typing replace both this and the converter
    """
    grok.adapts(
                          zope.interface.Interface,
                          zope.interface.Interface,
                          zope.interface.Interface,  # Form
                          IList,          # field
                          DataGridField)             #widget
    grok.provides(IValidator)

    def validate(self, value):
        """
            Don't validate the table - however, if there is a cell error, make sure that
            the table widget shows it.
        """
        for subform in [widget.subform for widget in self.widget.widgets]:
            for widget in subform.widgets.values():
                if hasattr(widget, 'error') and widget.error:
                    raise ValueError(widget.label)
        return None
