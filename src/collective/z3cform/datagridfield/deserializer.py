from collective.z3cform.datagridfield.interfaces import IRow
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DatetimeFieldDeserializer
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from pytz import timezone
from pytz import utc
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFields
from zope.schema.interfaces import IDatetime

import dateutil


@implementer(IFieldDeserializer)
@adapter(IRow, IDexterityContent, IBrowserRequest)
class DatagridRowDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        row_data = {}

        for name, field in getFields(self.field.schema).items():
            if field.readonly:
                continue

            if IDatetime.providedBy(field):
                # use the overriden deserializer to get the right
                # datamanager context
                context = self.field
            else:
                context = self.context

            deserializer = queryMultiAdapter(
                (field, context, self.request), IFieldDeserializer
            )
            if deserializer is None:
                # simply add value
                if name in value:
                    row_data[name] = value[name]
                continue

            row_data[name] = deserializer(value[name])

        return row_data


# We override DatetimeDeserializer because of the IDatamanager context
# in a DatagridField the context is the field not the dexterity type
@implementer(IFieldDeserializer)
@adapter(IDatetime, IRow, IBrowserRequest)
class DatagridDatetimeDeserializer(DatetimeFieldDeserializer):
    def __call__(self, value):
        # TODO: figure out how to get tsinfo from current context
        tzinfo = None

        # see plone.restapi.deserializer.dxfields
        # This happens when a 'null' is posted for a non-required field.
        if value is None:
            self.field.validate(value)
            return

        # Parse ISO 8601 string with dateutil
        try:
            dt = dateutil.parser.parse(value)
        except ValueError:
            raise ValueError(f"Invalid date: {value}")

        # Convert to TZ aware in UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(utc)
        else:
            dt = utc.localize(dt)

        # Convert to local TZ aware or naive UTC
        if tzinfo is not None:
            tz = timezone(tzinfo.zone)
            value = tz.normalize(dt.astimezone(tz))
        else:
            value = utc.normalize(dt.astimezone(utc)).replace(tzinfo=None)

        self.field.validate(value)
        return value
