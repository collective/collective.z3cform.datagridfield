from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='collective.z3cform.datagridfield',
      version=version,
      description="Version of DataGridField for use with Dexterity / z3c.form",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone, Dexterity, z3c.form',
      author='Kevin Gill',
      author_email='kevin@movieextras.ie',
      url='https://github.com/collective/collective.z3cform.datagridfield',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'five.grok',
          'plone.app.z3cform',
          'plone.directives.form',
          'setuptools',
          'z3c.form >=2.4.3dev',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'collective.z3cform.datagridfield_demo',
              'unittest2',
              'transmogrify.dexterity',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
