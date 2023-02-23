# -*- coding: utf-8 -*-
"""
    Demo of the widget
"""
from ..blockdatagridfield import BlockDataGridFieldWidgetFactory
from ..datagridfield import DataGridFieldWidgetFactory
from ..row import DictRow
from datetime import datetime
from plone.autoform.directives import widget
from plone.autoform.form import AutoExtensibleForm
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.interface import Interface


# Uncomment, if you want to try the relationfield
# from plone.app.vocabularies.catalog import CatalogSource
# from z3c.relationfield.schema import RelationChoice


class IAddress(Interface):
    line1 = schema.TextLine(title="Line 1", required=True)
    address_type = schema.Choice(
        title="Address Type", required=True, values=["Work", "Home"]
    )
    # Uncomment, if you want to try the relationfield
    #    link = RelationChoice(
    #        title=u"Link to content",
    #        source=CatalogSource(portal_type=['Document']),
    #        required=True
    #    )
    line2 = schema.TextLine(title="Line 2", required=False)
    city = schema.TextLine(title="City / Town", required=True)
    country = schema.TextLine(title="Country", required=True)
    frozenField = schema.TextLine(title="Don't change", readonly=True, required=False)

    # A sample integer field
    personCount = schema.Int(
        title="Persons",
        description="Enter number of persons (min 0 and max 15)",
        required=False,
        min=0,
        max=15,
    )

    dateAdded = schema.Datetime(title="Date added")

    # A sample checkbox
    billed = schema.Bool(title="Billed")


class IPerson(Interface):
    """
    Note: when using a dict, it is still an object - A schema.Dict would be
    expected to contain some schemas. We are using an object implemented
    as a dict
    """

    name = schema.TextLine(title="Name", required=True)
    address = schema.List(
        title="Addresses",
        value_type=DictRow(title="Address", schema=IAddress),
        required=True,
    )
    widget(address=DataGridFieldWidgetFactory)


TESTDATA = {
    "name": "MY NAME",
    "address": [
        {
            "address_type": "Work",
            "line1": "My Office",
            "line2": "Big Office Block",
            "city": "Mega City",
            "country": "The Old Sod",
            "personCount": 2,
            "dateAdded": datetime(1981, 8, 17, 0o6, 00, 00),
            "billed": False,
            "frozenField": "do not change!",
        },
        {
            "address_type": "Home",
            "line1": "Home Sweet Home",
            "line2": "Easy Street",
            "city": "Burbs",
            "country": "The Old Sod",
            "personCount": 4,
            "dateAdded": datetime(1981, 8, 17, 0o6, 00, 00),
            "billed": True,
            "frozenField": "do not change!",
        },
    ],
}


class EditForm(AutoExtensibleForm, form.EditForm):
    label = "Simple Form"
    schema = IPerson
    show_note = False

    def getContent(self):
        return TESTDATA

    def dumpOutput(self, data):
        """
        Helper function to see what kind of data DGF submits.
        """
        address = data.get("address", [])

        print("Dumping out extracted addresses")
        for entry in address:
            print(entry)

        print("Dumping out raw HTTP POST form data")
        for k, v in self.request.form.items():
            print("%s: %s" % (k, v))

    @button.buttonAndHandler("Save", name="save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.dumpOutput(data)

        context = self.getContent()
        for k, v in data.items():
            context[k] = v

    def updateActions(self):
        """Bypass the baseclass editform - it causes problems"""
        super().updateActions()

    def datagridUpdateWidgets(self, subform, widgets, widget):
        pass

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].allow_reorder = True


class EditForm2(EditForm):
    label = "Hide the Row Manipulators"

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].allow_insert = False
        self.widgets["address"].allow_delete = False


class EditForm3(EditForm):
    label = "Disable Auto-append"

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].auto_append = False


class EditForm4(EditForm):
    label = "Omit a column"

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].columns = [
            c for c in self.widgets["address"].columns if c["name"] != "country"
        ]

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit("country")


class EditForm5(EditForm):
    label = "Configure Subform Widgets"

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets["line1"].size = 40
        widgets["line2"].size = 40
        widgets["city"].size = 20
        widgets["country"].size = 10


class EditForm6(EditForm):
    label = "Hide a Column"

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets["city"].mode = HIDDEN_MODE

    def updateWidgets(self):
        # This one hides the column title
        super().updateWidgets()
        self.widgets["address"].columns[3]["mode"] = HIDDEN_MODE


class EditForm7(EditForm):
    label = "Table is read-only, cells editable"
    show_note = True

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].mode = DISPLAY_MODE


class EditForm8(EditForm):
    label = "Table and cells are read-only"

    def updateWidgets(self):
        super().updateWidgets()
        self.widgets["address"].mode = DISPLAY_MODE
        for wdt in self.widgets["address"].widgets:
            wdt.mode = DISPLAY_MODE


class IPersonBlocked(IPerson):
    widget(address=BlockDataGridFieldWidgetFactory)


class EditForm9(EditForm):
    label = "Block widgets as blocks instead of cells"
    schema = IPersonBlocked
