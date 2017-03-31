*** Setting ***
Library           Selenium2Library
Library           TestUtils

*** Variable ***
${ENVIRONMENT}    atest
${BROWSER}    ff
${SeleniumTimeout}    30
${URL_local}  http://localhost:3880/
${URL_atest}  http://localhost:3880/

*** Keyword ***
Choose Git Repository
    [Arguments]    ${url}
    Input text    repo_url    ${url}
    Click Button    nappula

    #Wait Until Element is Visible  xpath=//text[contains(text(), 'https://github.com/wikimedia/WikipediaMobile.git')]
    Wait Until Element is Visible  xpath=//button[contains(text(), 'Chart Type')]
    Capture Page Screenshot

Verify Value
    [Arguments]    ${value}
    Wait until keyword succeeds    120    5    odota pallukkaa

Odota pallukkaa
    Reload page
    Wait Until Page Contains Element  xpath=//*[name()='circle']    timeout=5s

###############################
# UTILITIES
###############################

Prepare Environment
    Set Suite Variable    ${URL}    ${URL_${ENVIRONMENT}}
    Prepare Browser
    # ${revision}=    Get Text   revision-info
    # Log    ${revision}

Prepare browser
    Set Selenium Timeout    ${SeleniumTimeout}
    # Set Screenshot Directory    reports/pics    True
    Open Browser    about:blank     browser=${BROWSER}
    Delete All Cookies
    Go To    ${URL}
    Location Should Contain    ${URL}
    Maximize Browser Window

Reset Browser
    Comment  Resetting browser
    # Close OS Browsers
    # Prepare Browser

Cleanup environment
    Close OS Browsers
