*** Setting ***
Library           Selenium2Library
Library           TestUtils
Resource          TestApi.robot

*** Keyword ***

###############################
# ACTIONS
###############################

As ${me}, choose repository ${url}
    [Documentation]    Choose repository by entering new url and pressing submit
    Choose Git Repository    ${url}

###############################
# VERIFICATIONS
###############################
As ${me}, verify graph
    [Documentation]    Verifies graph data
    Verify Value    foo
