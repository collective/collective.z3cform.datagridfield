from setuptools import setup


version = "4.0.0a1"


setup(
    name="collective.z3cform.datagridfield",
    # zest.releaser needs version here for now
    version=version,
    description="Fields with repeatable data grid (table-like) for z3.cform",
    long_description="\n\n".join(
        [
            open("README.rst").read(),
            open("CHANGES.rst").read(),
        ]
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone z3cform table data grid",
    author="Kevin Gill",
    author_email="kevin@movieextras.se",
    url="https://github.com/collective/collective.z3cform.datagridfield",
    license="GPLv2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Products.GenericSetup",
        "plone.app.dexterity",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.base",
        "plone.dexterity",
        "plone.restapi",
        "plone.supermodel",
        "z3c.form >= 4.0",
    ],
    extras_require={
        "test": [
            "plone.testing",
            "plone.app.testing",
            "plone.app.robotframework[debug]",
            "robotsuite",
            "robotframework-browser",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
