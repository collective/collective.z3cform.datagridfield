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
from z3c.form.interfaces import NOT_CHANGED
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


def _get_stored(stored_row, name, fld):
    """Return the pre-POST stored value for a row column.

    Accepts either a dict-like ObjectWidgetValue or a plain dict.
    Falls back to ``fld.missing_value`` when no stored value is found.
    """
    if not stored_row:
        return fld.missing_value
    try:
        val = stored_row.get(name, fld.missing_value)
    except AttributeError:
        val = getattr(stored_row, name, fld.missing_value)
    if val is NO_VALUE:
        return fld.missing_value
    return val


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

    def _getFieldConverter(self, name, fld):
        """Return the converter for a sub-field.

        Prefer the converter registered for the actual sub-widget (which may
        be a custom widget set via a ``directives.widget`` declaration, e.g.
        ``LinkWidget``, ``NamedImageWidget``). Only if no row sub-widget is
        available (e.g. before ``updateWidgets``), fall back to the default
        converter for the field type.
        """
        sub_widget = None
        actual_widgets = getattr(self.widget, "widgets", None)
        if actual_widgets:
            sub_widget = actual_widgets.get(name)
        if sub_widget is not None:
            converter = queryMultiAdapter((fld, sub_widget), IDataConverter)
            if converter is not None:
                return converter, sub_widget
        return self._getConverter(fld), sub_widget

    def toFieldValue(self, value):
        _converted = {}
        # The pre-POST stored row (dict) is stamped onto the row widget by
        # DataGridFieldWidget.getWidget. Used to resolve NOT_CHANGED results
        # from sub-converters (e.g. NamedDataConverter on action=nochange)
        # and NO_VALUE raw extractions from sub-widgets that had no access
        # to the context (e.g. NamedFileWidget extracted by the fresh row
        # widgets built inside MultiWidget.extract).
        stored_row = getattr(self.widget, "_stored_row", None) or {}
        for name, fld in self.field.schema.namesAndDescriptions():
            if fld.readonly:
                continue
            converter, sub_widget = self._getFieldConverter(name, fld)
            val = value.get(name, fld.default)
            # NO_VALUE must never reach a sub-converter: most converters
            # (e.g. NamedDataConverter) cannot cope with the sentinel. It
            # appears when a sub-widget had no data and no context to fall
            # back on - treat it as "keep the stored value", matching the
            # semantics of NOT_CHANGED.
            if val is NO_VALUE:
                _converted[name] = _sanitize_field_value(
                    fld, _get_stored(stored_row, name, fld)
                )
                continue
            try:
                converted = converter.toFieldValue(val)
            except Exception:
                # Defensive: never let a single column break row storage.
                logger.warning(
                    "Error converting value for column %r in DictRow: %r (%s)",
                    name,
                    val,
                    type(val),
                )
                _converted[name] = val
                continue

            if converted is NOT_CHANGED:
                # Keep the previously stored value (e.g. NamedFile nochange).
                converted = _get_stored(stored_row, name, fld)
            if converted is NO_VALUE:
                # NO_VALUE is a non-picklable sentinel - never store it.
                converted = fld.missing_value
            _converted[name] = _sanitize_field_value(fld, converted)
        return _converted

    def toWidgetValue(self, value):
        _converted = {}
        for name, fld in self.field.schema.namesAndDescriptions():
            converter, _sub_widget = self._getFieldConverter(name, fld)
            val = value.get(name, fld.default)
            # NO_VALUE can appear here if a previous (buggy) save persisted
            # it. Normalize to missing_value before handing it to the
            # sub-converter, which typically cannot cope with the sentinel.
            if val is NO_VALUE:
                val = fld.missing_value
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
