# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '1.4.0'

setup(
    name='collective.z3cform.datagridfield',
    version=version,
    description="Version of DataGridField for use with Dexterity / z3c.form",
    long_description=(
        open("README.rst").read() +
        '\n' +
        open("CHANGES.rst").read()
    ),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
    ],
    keywords='Plone, Dexterity, z3c.form',
    author='Kevin Gill',
    author_email='kevin@movieextras.ie',
    url='https://github.com/collective/collective.z3cform.datagridfield',
    license='GPL',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.z3cform'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.app.z3cform',
        'plone.autoform',
        'Products.CMFPlone',
        'plone.api',
        'setuptools',
        'z3c.form >=2.4.3dev',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
