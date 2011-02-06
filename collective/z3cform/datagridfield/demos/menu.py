"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from five import grok

from zope.interface import Interface
from zope import schema

from z3c.form import field
from z3c.form.widget import FieldWidget
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE

from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DataGridField


class Menu(grok.View):
    grok.context(Interface)
    grok.name('demo-collective.z3cform.datagrid-menu')
