from collective.z3cform.datagridfield.testing import FUNCTIONAL_TESTING
from plone.testing.zope import Browser

import unittest


class TestDemoDGFForm(unittest.TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        # see ../demo/editform_simple.py module
        self.demo_form = self.browser.open(
            f"{self.portal.absolute_url()}/@@demo-collective.z3cform.datagrid"
        )

    def test_datarow_0(self):
        column_data = [
            ("address_type:list", ["Work"], True),
            ("line1", "My Office", True),
            ("line2", "Big Office Block", False),
            ("city", "Mega City", True),
            ("country", "The Old Sod", True),
        ]

        for name, value, required in column_data:
            ctrl = self.browser.getControl(
                name=f"form.widgets.address.0.widgets.{name}"
            )
            self.assertEqual(ctrl.value, value)
            self.assertEqual("required" in str(ctrl._elem), required)

    def test_autoinsert_row(self):
        column_data = [
            ("address_type:list", ["--NOVALUE--"], False),
            ("line1", "", False),
            ("line2", "", False),
            ("city", "", False),
            ("country", "", False),
        ]

        for name, value, required in column_data:
            ctrl = self.browser.getControl(
                name=f"form.widgets.address.AA.widgets.{name}"
            )
            self.assertEqual(ctrl.value, value)
            self.assertEqual("required" in (ctrl._elem), required)

    def test_template_row(self):
        column_data = [
            ("address_type:list", ["--NOVALUE--"], False),
            ("line1", "", False),
            ("line2", "", False),
            ("city", "", False),
            ("country", "", False),
        ]

        for name, value, required in column_data:
            ctrl = self.browser.getControl(
                name=f"form.widgets.address.TT.widgets.{name}"
            )
            self.assertEqual(ctrl.value, value)
            self.assertEqual("required" in (ctrl._elem), required)

    def test_buttons(self):
        # Make sure the add row button is present (x4)
        self.assertEqual(self.browser.contents.count("dgf--row-add"), 4)
        # Make sure the delete row button is present (x4)
        self.assertEqual(self.browser.contents.count("dgf--row-delete"), 4)

    def test_description(self):
        # Make sure the description is displayed in the 'personCount' column header
        self.assertTrue(
            "Enter number of persons (min 0 and max 15)" in self.browser.contents
        )

    def test_resource_url(self):
        # Make sure resources from our package are not using absolute URLs.  If absolute
        # URLs are present, then the resources won't load on anything except where
        # Plone/Zope are the root of the domain.
        self.assertTrue(
            '"/++resource++collective.z3cform.datagridfield'
            not in self.browser.contents
        )
