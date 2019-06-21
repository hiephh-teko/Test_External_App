
import os
from dotenv import load_dotenv

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(_DOT_ENV_PATH)

from unittest import mock
from tests.jira import JiraService
import pytest



@pytest.fixture
def headers():
    """Fixture header when call to apis"""
    mimetype = 'application/json'
    _headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    return _headers


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'test_outcome', rep)


@pytest.fixture(scope='class')
def jira_test_service():
    return JiraService()


@pytest.fixture(scope='class')
def jira_test_suite(request, jira_test_service):
    cls = request.cls
    cls.results = {}
    cls.tests_list = []

    submit_tests = request.config.getoption('--submit-tests', default=False)
    
    if not getattr(cls, 'ISSUE_KEY', None):
        submit_tests = False

    if submit_tests:
        cls.tests_list = jira_test_service.get_tests_in_issue(cls.ISSUE_KEY)

    yield

    if submit_tests:
        def find_existed_test(test_name):
            tests_key_match = [
                test_key for (test_name, test_key) in cls.tests_list
                if name == test_name
            ]
            return None if len(tests_key_match) == 0 else tests_key_match[0]

        # Create test keys
        for name in cls.results:
            test_key = find_existed_test(name)
            if not test_key:
                test_key = jira_test_service.create_test(name, cls.ISSUE_KEY)
            cls.results[name]['testCaseKey'] = test_key
        test_cycle_items = [v for k, v in cls.results.items()]

        # Create test cycle
        jira_test_service.create_test_cycle(
            cls.ISSUE_KEY + ' - ' + cls.__name__, cls.ISSUE_KEY,
            test_cycle_items)

        # Clean up deprecated test names
        for test_name, test_key in cls.tests_list:
            if test_name not in cls.results.keys():
                jira_test_service.delete_test(test_key)

@pytest.fixture()
def update_test_result(request):
    MAX_NAME_LENGTH = 255
    name = request._pyfuncitem.name
    if len(name) > MAX_NAME_LENGTH:
        name = name[0:255]

    request.cls.results[name] = {'status': 'Pass'}
    yield
    if request.node.test_outcome.failed:
        request.cls.results[name]['status'] = 'Fail'


def pytest_addoption(parser):
    parser.addoption(
        '--submit-tests',
        action='store_true',
        help='Submit tests to Jira'
    )
