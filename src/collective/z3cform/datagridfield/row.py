from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from collective.z3cform.datagridfield.interfaces import AttributeNotFoundError
from collective.z3cform.datagridfield.interfaces import IRow
from plone.app.dexterity.permissions import DXFieldPermissionChecker
from plone.app.dexterity.permissions import GenericFormFieldPermissionChecker
from plone.app.z3cform.interfaces import IFieldPermissionChecker
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from z3c.relationfield.interfaces import IRelation
from z3c.relationfield.interfaces import IRelationList
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema import Field
from zope.schema import getFields
from zope.schema import Object
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import WrongContainedType
from zope.security.interfaces import IPermission

import logging

logger = logging.getLogger(__name__)


def _sanitize_field_value(fld, value):
    """Strip acquisition wrappers from a converted field value.

    ContentBrowserDataConverter returns acquisition-wrapped content objects
    for RelationList/RelationChoice fields. Storing these in ZODB fails with
    'Can't pickle objects in acquisition wrappers'. Stripping the wrapper
    stores a plain ZODB persistent reference instead, which is picklable and
    still usable by IUUID() in toWidgetValue.
    """
    if value is None:
        return value
    if IRelationList.providedBy(fld):
        if not value:
            return value
        return type(value)(aq_base(item) for item in value if item is not None)
    if IRelation.providedBy(fld):
        return aq_base(value)
    return value


@implementer(IRow)
class DictRow(Object):
    __doc__ = IRow.__doc__
    _type = dict

    def _validate(self, value):
        # XXX HACK: Can't call the super, since it'll check to
        # XXX see if we provide DictRow.
        # We're only a dict, so we can't.
        # super()._validate(value)

        # Validate the dict against the schema
        # Pass 1 - ensure fields are present
        if value is NO_VALUE:
            return
        # Treat readonly fields
        for field_name in list(getFields(self.schema).keys()):
            field = self.schema[field_name]
            if field.readonly:
                value[field_name] = field.default
        errors = []
        for field_name in list(getFields(self.schema).keys()):
            if field_name not in value:
                errors.append(AttributeNotFoundError(field_name, self.schema))

        if errors:
            raise WrongContainedType(errors, self.__name__)

        # Pass 2 - Ensure fields are valid
        for field_name, field_type in list(getFields(self.schema).items()):
            if IChoice.providedBy(field_type):
                # Choice must be bound before validation otherwise
                # IContextSourceBinder is not iterable in validation
                bound = field_type.bind(self.context)
                bound.validate(value[field_name])
            else:
                field_type.validate(value[field_name])

    def set(self, object, value):
        # Override Object field logic
        Field.set(self, object, value)


@adapter(IRow, IFieldWidget)
class DictRowConverter(BaseDataConverter):
    # convert the columns to their field/widget value

    def toFieldValue(self, value):
        _converted = {}
        for name, fld in self.field.schema.namesAndDescriptions():
            if fld.readonly:
                # skip readonly columns
                continue
            converter = self._getConverter(fld)
            val = value.get(name, fld.default)
            if val is NO_VALUE:
                # NO_VALUE is a non-picklable sentinel from z3c.form that
                # widgets (e.g. LinkWidget) return for empty fields. It must
                # never be stored persistently, so map it to missing_value.
                _converted[name] = fld.missing_value
                continue
            try:
                _converted[name] = _sanitize_field_value(
                    fld, converter.toFieldValue(val)
                )
            except Exception:
                # XXX: catch exception here in order to not break
                # versions prior to this fieldValue converter
                logger.warning(
                    f"Error converting value for column '{name}' in DictRow: {val!r} ({type(val)})"
                )
                _converted[name] = val
        return _converted

    def toWidgetValue(self, value):
        _converted = {}
        # Use the actual sub-widgets if they are already set up on the row
        # widget (e.g. LinkWidget instead of the default TextWidget).
        # This ensures that converters for custom widgets (like
        # LinkWidgetDataConverter) are used, which may expect/return a dict.
        actual_widgets = getattr(self.widget, "widgets", {})
        for name, fld in self.field.schema.namesAndDescriptions():
            sub_widget = actual_widgets.get(name) if actual_widgets else None
            if sub_widget is not None:
                converter = queryMultiAdapter((fld, sub_widget), IDataConverter)
            else:
                converter = None
            if converter is None:
                converter = self._getConverter(fld)
            val = value.get(name, fld.default)
            try:
                _converted[name] = converter.toWidgetValue(val)
            except Exception:
                # XXX: catch exception here in order to not break
                # versions prior to this widgetValue converter
                _converted[name] = val
        return _converted


@adapter(IDexterityContent)
@implementer(IFieldPermissionChecker)
class DictRowFieldPermissionChecker(DXFieldPermissionChecker):
    # override plone.app.dexterity.permissions.DXFieldPermissionChecker
    # to check the permission of the parent field instead of the
    # field in DictRow. This is needed to enable vocabulary/source lookups in
    # plone.autoform schema hint widgets
    # XXX: this has to be registered in overrides.zcml

    def validate(self, field_name, vocabulary_name=None):
        try:
            return super().validate(field_name, vocabulary_name)
        except AttributeError as orig_exception:
            # field_name is not found in base schema
            # check possible DataGridFieldObjectWidget schematas

            checker = getSecurityManager().checkPermission
            context = self.context

            for schema in self._get_schemata():
                for fld_name, fld in schema.namesAndDescriptions():
                    dict_row = getattr(fld, "value_type", None)
                    if (
                        not isinstance(dict_row, DictRow)
                        or field_name not in dict_row.schema
                    ):
                        continue

                    # check the permission of the DictRow field
                    field = dict_row.schema[field_name]
                    if not self._validate_vocabulary_name(
                        dict_row.schema, field, vocabulary_name
                    ):
                        return False

                    # Create mapping of all schema permissions
                    permissions = mergedTaggedValueDict(
                        dict_row.schema, WRITE_PERMISSIONS_KEY
                    )
                    permission_name = permissions.get(field_name, None)
                    if permission_name is not None:
                        # if we have explicit permissions, check them
                        permission = queryUtility(IPermission, name=permission_name)
                        if permission:
                            return checker(permission.title, context)

                    # If the field is in the schema, but no permission is
                    # specified, fall back to the default edit permission
                    return checker(self.DEFAULT_PERMISSION, context)
            else:
                raise orig_exception


class GenericFormDictRowFieldPermissionChecker(
    DictRowFieldPermissionChecker, GenericFormFieldPermissionChecker
):
    """same override as above for ++add++ forms"""
