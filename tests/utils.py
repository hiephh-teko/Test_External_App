import pytest


@pytest.mark.usefixtures('each_test_suite', 'each_test_case')
class JiraTest:
    pass