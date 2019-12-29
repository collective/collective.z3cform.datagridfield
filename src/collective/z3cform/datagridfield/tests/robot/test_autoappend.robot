# Run this robot test stand-alone:
#
#  $ bin/test -s collective.z3cform.datagridfield -t test_autoappend.robot --all
#

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Suite setup  Set Selenium speed  0.5s

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: Demo with two data rows plus empty row
    Given the demo
    Then two rows plus empty row are visible

Scenario: Add only one row
    Given the demo
    When I enter a value for first field
    Then one single row is added


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

the demo
    Go To  ${PLONE_URL}/@@demo-collective.z3cform.datagrid
    Wait until page contains  Country


# --- WHEN -------------------------------------------------------------------

I enter a value for first field
    Wait until element is visible
    ...  id=form-widgets-address-2-widgets-line1
    Input Text  form-widgets-address-2-widgets-line1  Chalet in the mountains
    Input Text  form-widgets-address-2-widgets-line2  Valais


# --- THEN -------------------------------------------------------------------

two rows plus empty row are visible
    Element Should Be Visible  id=form-widgets-address-0-widgets-line1
    Element Should Be Visible  id=form-widgets-address-1-widgets-line1
    Element Should Be Visible  id=form-widgets-address-2-widgets-line1
    Element Should Not Be Visible  id=form-widgets-address-3-widgets-line1

one single row is added
    Element Should Be Visible  id=form-widgets-address-3-widgets-line1
    Element Should Not Be Visible  id=form-widgets-address-4-widgets-line1
