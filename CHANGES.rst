Changelog
=========

1.4.0 (2019-02-21)
------------------

- Added missing upgrade step, calling browserlayer setup.
  [sgeulette]

- Display column description if provided in schema `field.description`.
  [gbastien, bleybaert]

- Specify in README.rst that versions >= 1.4 are for Plone 5+ and
  versions < 1.4 are for Plone 4.
  [gbastien]

- Usability change: add an (hidden) label inside the add commands
  [keul]

- Compatibility with Plone 5 modals/overlay from mockup
  [keul]

1.3.1 (2019-02-21)
------------------

- Extend uninstall profile.
  [thet]

- Wrapped commands inside ``A`` tags, required for accessibility reason (change backported from Products.DataGridField).
  This also simplify customizing icons with pure CSS.
  [keul]

- Replaced minus icon with a more usable delete icon.
  [keul]

- Removed ols-school ``*`` chars for marking fields as required.
  [keul]

- Fix object access
  [tomgross]

- Fix usage of related items widget in subforms
  https://github.com/plone/Products.CMFPlone/issues/2446
  [tomgross]

1.3.0 (2017-11-22)
------------------

- Set widget mode on cell widget in order to support autoform mode directive. [jone]

- Bugfix: do not try to update readonly fields. [jone]

- Cleanup: utf8 headers, isort, code-style. [jensens]

- Remove dependency on plone.directives.form in setup.py,
  it was not used any longer. [jensens]

- Feature/Fix: Support widgets using patternslib in a DictRow.
  [jensens]

- Fix: #36 remove grok from all documentation since grok is no longer supported.
  [jensens]

- Copy relevant parts of ObjectSubform from z3c.form 3.2.10 over here, it was removed in later versions.
  [jensens]

- Add Browserlayer and use it, also add uninstall step.
  [jensens]

- Move Demo package to in here.
  [jensens]


1.2 (2017-03-08)
----------------

- Fix validation exception on readonly fields.
  [rodfersou]
- Fix bug for widget.klass is NonType in the block view when defining the class for the field.
- Allow deletion of last row in non-auto-append mode.
  [gaudenz]
- fixed binding for IChoice fields during validation [djay]
- plone 5 compatibility and fixed travis testing for plone 5 [djay]


1.1 (2014-07-25)
----------------

- Removed JS code that relies on firefox being used.
  [neilferreira]

- Stopped referencing the 'event' element when creating a new row as the event
  that triggered the content of an input changing may have been from another element.
  [neilferreira]


1.0 (2014-06-02)
----------------

- Add 'form-widgets-field_id' as widget css id (consistency with other widgets).
  [thomasdesvenain]

- Fix package dependencies.
  [hvelarde]

- Use BlockDataGridFieldObject for rows in a BlockDataGridField.
  [gaudenz]

- Filter out any auto append or template rows in updateWidgets.
  [gaudenz]

- Add row parameter to aftermoverow JS event
  [gaudenz]

- Don't reset class attribute on cloned template rows
  [gaudenz]

- Replace row index in all template row elements, not just input elements.
  Replace the index in id, name, for, href and data-fieldname attributes
  when cloning the template row.
  [gaudenz]


0.15 (2013-09-24)
-----------------

- Added possibility to define the CSS class for the main table when the field is displayed.
  This way, you can use common Plone existing classes (like 'listing').
  [gbastien]

- Fixed auto-append bug when there is more than one datagrid field in page auto-appending one field binds
  "change.dgf" to another field also. added "$(dgf).find(.." in datagridfield.js line 138 so it binds to right element only.
  [tareqalam]

- Only abort moveRow if the row is really not found and not if the row idx just happens to be 0.
  [gaudenz]

- Also update hidden data rows when reindexing in row mode. This fix was previously somehow only done for block mode.
  [gaudenz]

- Relax requirements for markup, don't assume inputs are direct childs of table cells. This makes useing custom
  templates much easier.
  [gaudenz]

- Fix validate function signature for IValidator API. The API requires a "force" argument.
  [gaudenz]

- Register the SubformAdapter for IPloneForm layer to avoid that the Adapter from plone.app.z3cform
  takes precedence.
  [gaudenz]


0.14 (2013-05-24)
-----------------

- Align travis setup to other packages.
  [saily]

- Add new V1 ``bootstrap.py``.
  [saily]

- Added CSS classes to tbody rows (``row-(1...n)``) and thead columns
  (``cell-(1...m)``) to allow more styling in edit forms.
  [saily]

- Fixed wrong template in display mode when set editing to block edit mode [miohtama]

- Added CSS classes (widget.klass attribute) for DataGridField, to separate it from other MultiWidgets [miohtama]


0.13 (2013-04-09)
-----------------

- Add travis-ci configs [jaroel]

- Convert tests to plone.app.testing [jaroel]

- Fix to expect ``zope.schema.interfaces.ValidationError`` to work better
  with *TooLong* and *TooShort* exceptions. [datakurre]

- Fix IE7 failing on `<label>` for manipulation [miohtama]

- Deal with situations where there is zero rows on DGF and no auto-append row available [miohtama]

- Correctly bind DGF events on DOM content loaded, not when Javascript is parsed [miohtama]

- Don't display movement handles if the row cannot be moved [miohtama]

- Changed move up and down handlers to stay in fixed positions to make cells stay in the same width regardless of moving [miohtama]

- Fixed checkbox saving, was broken by nested DGF support [miohtama]

- Added block edit mode [miohtama]

- "use strict;" and ECMAScript 5 compatible Javascript clean-up [miohtama]

- Added *afterrowmoved* JS event [miohtama]


0.12 (2012-10-30)
--------------------

- Updated empty row selection. [jstegle]

- Nested DataGridField support (yo dawg...) [miohtama]

- Support plone.autoform and grok'ed row schemas [miohtama]

- Added ``DataGridField.extra`` parameter, so you can pass out
  application specific data to Javascript [miohtama]


0.11 (2012-05-16)
-----------------

- be able to use with plone.app.registry
  [vangheem]


0.10 (2012-02-12)
-----------------

- Fix bug with moving the last row up.
  [m-martinez]


0.9 (2011-10-27)
----------------

- Clone events when adding new row - fixes bug where browse button of
  plone.formwidget.contenttree did nothing for new rows
  [anthonygerrard]

- Reindex more indexed attributes of cloned row
  [anthonygerrard]


0.8 (2011-09-24)
----------------

- Avoid using the "row" CSS class.
  [davisagli]

- Fixes to work with jQuery 1.3.x (use .remove() instead of .detach(), fetch data
  attributes a different way, and avoid live binding the change event).
  [davisagli]

- Don't error out when getting a ``FormatterValidationError``, pass
  it on to z3c.form instead.
  [claytron]

- Give manipulator images a relative src rather than absolute. This
  previously meant the widget didn't work on sites without Plone/Zope at the
  root of the domain.
  [davidjb]

- During auto-insert, add our new row into the document first, before reindexing
  it and changing its elements' IDs. This allows Javascript that depends on
  these IDs (such as plone.formwidget.autocomplete) to pick up the correct
  fields.
  [davidjb]

- Tidying up and reducing complexity of auto-insert functionality
  [davidjb]

- Removing unnecessary auto-insert bind and unbind as this is already covered
  by jQuery's `live()` function against the `auto-append` class. Adding/removing
  this class against rows automatically does this.
  [davidjb]

- Resolved issue with auto-insert functionality not working by removing
  table-specific check in Javascript.
  [davidjb]


0.7 (2011-07-01)
----------------

- Changed markup/javascript to prevent duplicate HTML id attributes. Changed
  Javascript to allow for datagrid page templates that don't use tables.
  [dextermilo]

- Improve spacing in CSS.
  [davisagli]

- Revert my fix to ensure that blank rows are added, because it duplicated
  a fix in z3c.form resulting in extra rows.
  [davisagli]


0.6 (2011-05-17)
----------------

- Search for datagridInitialise and datagridUpdateWidgets on the
  parent form, also when in a fieldset.
  [maurits]

- Register templates on plone.app.z3cform.interfaces.IPloneFormLayer to
  take precedence over that packages list widget templates.
  [elro]

- Make sure that updateWidgets is called to add blank rows even if the
  widget has no value.
  [davisagli]

- When extracting a row value fails due to a validation error, convert
  widget values to field values so the value can be successfully applied
  to the grid widget.
  [davisagli]

- Register a plone.supermodel handler for the DictRow so it can be used
  in supermodel models.
  [davisagli]

- Depend on collective.z3cform.datagridfield_demo as a test extra;
  use the browser view from this package in the tests.
  [maurits]

- _validate still used when import/exporting, fix up code so it works
  [lentinj]

- Add a DictRow serializer for transmogrify.dexterity
  [lentinj]

- Only use width:100% on input cells that are the only element in the cell
  [lentinj]

- Reorder row indices backwards when adding rows. This means that adjacent
  rows don't share the same index temporarily, for example:-
  - Row 1 and 2 contain input:radio based widgets
  - Row 0 added, row renumbering starts
  - Row 1 widgets renamed 2
  - Both sets of input:radio share the same name, one deselected
  - Row 2 widgets renamed 3
  - . . .
  [lentinj]

- Use jQuery to clone rows, and clone the jQuery events on the rows.
  [lentinj]

- Implemented reorder functionality


0.5 (2011-02-08)
----------------

- Put in the DictRow class (tks Martin Aspeli)

- Moved the demo code out to a separate package collective.z3cform.datagridfield_demo
  (tks Laurence Rowe).

- Removed superfluous lines from setup.py (tks Laurence Rowe).

- Removed unnessary dependency on dexterity (tks Laurence Rowe).

- Removed unnessary dependency on grok (tks Laurence Rowe).


0.4 (2011-02-06)
----------------

- Renamed the demo pages. The starting point is now @@demo-collective.z3cform.datagrid .

- The widget can now be configured via the updateWidgets method. It
  is no longer necessary to create a custom factory.

- The columns can now be omitted.

- Provide a set of demo views for Object access.


0.3 (2011-02-04)
----------------

- The auto-append functionality did not bind correctly for popup forms.
  I switched to using jQuery.live() instead of binding at document load time.

- Added a menu to the demo pages

- Added a display only form option.

- Fixed the restructured text of the main README.txt so that it will show
  more friendly in PyPI.
