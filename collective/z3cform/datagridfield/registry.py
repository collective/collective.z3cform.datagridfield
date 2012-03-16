from collective.z3cform.datagridfield import DictRow as BaseDictRow
try:
    from plone.registry.field import PersistentField
except ImportError:
    class PersistentField(object):
        pass


class DictRow(PersistentField, BaseDictRow):
    pass
