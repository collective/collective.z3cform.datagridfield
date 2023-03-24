# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import getSecurityManager
from collective.z3cform.datagridfield.interfaces import AttributeNotFoundError
from collective.z3cform.datagridfield.interfaces import IRow
from plone.app.dexterity.permissions import DXFieldPermissionChecker
from plone.app.z3cform.interfaces import IFieldPermissionChecker
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema import Field
from zope.schema import getFields
from zope.schema import Object
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import WrongContainedType
from zope.security.interfaces import IPermission


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
            try:
                _converted[name] = converter.toFieldValue(value[name])
            except Exception as msg:
                # XXX: catch exception here in order to not break
                # versions prior to this fieldValue converter
                _converted[name] = value[name]
        return _converted

    def toWidgetValue(self, value):
        _converted = {}
        for name, fld in self.field.schema.namesAndDescriptions():
            converter = self._getConverter(fld)
            try:
                _converted[name] = converter.toWidgetValue(value[name])
            except Exception as msg:
                # XXX: catch exception here in order to not break
                # versions prior to this widgetValue converter
                _converted[name] = value[name]
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
                        or not field_name in dict_row.schema
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
