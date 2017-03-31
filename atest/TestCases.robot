*** Setting ***
Suite Setup       Suite Setup
Suite Teardown    Cleanup Environment
Test Setup        Reset Browser
Test Timeout      3 minutes
Resource          Adaptation.robot
Resource          TestApi.robot

*** Test Case ***
Ismo views wikimedia repository
    [Tags]    GOOD
    As Ismo, choose repository https://github.com/wikimedia/WikipediaMobile.git
    As Ismo, verify graph

*** Keyword ***

Suite Setup
    Prepare Environment
