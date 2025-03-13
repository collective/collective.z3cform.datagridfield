# Run this robot test stand-alone:
#
#  $ bin/rfbrowser init chromium
#  $ bin/test -s collective.z3cform.datagridfield -t test_autoappend.robot --all
#

*** Settings *****************************************************************

Resource  plone/app/robotframework/browser.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Demo with two data rows plus empty row
    Given the demo
    Then two rows plus empty row are visible
     And I can submit

Scenario: Add only one row
    Given the demo
    When I enter a value for first field
    Then one single row is added

Scenario: Validate required field
    Given the demo
    When I remove the value for first field
    Then there is a validation error


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

the demo
    Go To  ${PLONE_URL}/@@demo-collective.z3cform.datagrid
    Wait For Condition    Text    //body    contains    Country


# --- WHEN -------------------------------------------------------------------

I enter a value for first field
    Wait For Elements State    //input[@id="form-widgets-address-AA-widgets-line1"]    visible
    Type Text    //input[@id="form-widgets-address-AA-widgets-line1"]    Chalet in the mountains
    Type Text    //input[@id="form-widgets-address-AA-widgets-line2"]    Valais

I remove the value for first field
    Wait For Elements State    //input[@id="form-widgets-address-AA-widgets-line1"]    visible
    Clear Text    //input[@id="form-widgets-address-0-widgets-line1"]


# --- THEN -------------------------------------------------------------------

two rows plus empty row are visible
    Wait For Elements State    //input[@id="form-widgets-address-0-widgets-line1"]    visible
    Wait For Elements State    //input[@id="form-widgets-address-1-widgets-line1"]    visible
    Wait For Elements State    //input[@id="form-widgets-address-AA-widgets-line1"]    visible
    Wait For Elements State    //input[@id="form-widgets-address-TT-widgets-line1"]    hidden

one single row is added
    Wait For Elements State    //input[@id="form-widgets-address-2-widgets-line1"]    visible
    Wait For Elements State    //input[@id="form-widgets-address-TT-widgets-line1"]    hidden

I can submit
    Click    //button[@id="form-buttons-save"]
    # Get Element Count    //em[@class="invalid-feedback"]    ==    0

There is a validation error
    Get Element Count    //tr[contains(@class, "row-1")]/td[contains(@class, "cell-1")]/em[@class="invalid-feedback"]    ==    1
