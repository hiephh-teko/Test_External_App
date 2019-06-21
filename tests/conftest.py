import os

from dotenv import load_dotenv

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(_DOT_ENV_PATH)

from unittest import mock
from datetime import datetime
from operator import itemgetter

import pytest
import requests


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'test_outcome', rep)


def pytest_addoption(parser):
    parser.addoption('--submit-tests',
                     action='store_true',
                     help='Submit tests to Jira')


class JiraTestService():
    def __init__(self, jira_settings):
        self.project_key = os.getenv('JIRA_PROJECT_KEY')
        self.auth_string = (os.getenv('JIRA_USER'), (os.getenv('JIRA_PASSWORD')))
        self.url = os.getenv('JIRA_URL') + '/rest/atm/1.0'

    def get_tests_in_issue(self, issue_key):
        params = {
            'query':
            'projectKey = "%s" AND issueKeys IN (%s)' %
            (self.project_key, issue_key)
        }
        response = requests.get(url=self.url + '/testcase/search',
                                params=params,
                                auth=self.auth_string).json()
        return list(map(itemgetter('name', 'key'), response))

    def create_test(self, test_name, issue_key):
        json = {
            'name': test_name,
            'projectKey': self.project_key,
            'issueLinks': [issue_key],
            'status': 'Approved'
        }
        response = requests.post(url=self.url + '/testcase',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test return with error status code',
                            response.status_code)

        test_key = response.json()['key']
        return test_key

    def delete_test(self, test_key):
        response = requests.delete(url=self.url + '/testcase/' + test_key,
                                   auth=self.auth_string)
        if response.status_code != 204:
            raise Exception('Delete test return with error status code',
                            response.status_code)

    def create_test_cycle(self, name, issue_key, items):
        def get_current_time():
            return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        json = {
            'name': name,
            'projectKey': self.project_key,
            'issueKey': issue_key,
            'plannedStartDate': get_current_time(),
            'plannedEndDate': get_current_time(),
            'items': items
        }
        response = requests.post(url=self.url + '/testrun',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test cycle return with error status code',
                            response.status_code)


def jira_test_service():
    return JiraTestService({
        'url': 'https://jira.teko.vn',
        'user': os.getenv('JIRA_USER'),
        'password': os.getenv('JIRA_PASSWORD'),
        'project_key': os.getenv('JIRA_PROJECT_KEY')
    })


delete_tests_on_issue = set()


@pytest.fixture(scope='class')
def each_test_suite(request):
    # Before each test suite
    cls = request.cls
    cls.results = {}
    cls.tests_list = []

    test_service = jira_test_service()  # Currently only support Jira

    submit_tests = request.config.getoption('--submit-tests', default=False)
    if not getattr(cls, 'ISSUE_KEY', None):
        submit_tests = False
    else:
        issue_info = test_service.get_issue_info(cls.ISSUE_KEY)
        if issue_info['fields']['status']['name'] == 'Closed':
            submit_tests = False

    if submit_tests:
        cls.tests_list = test_service.get_tests_in_issue(cls.ISSUE_KEY)

        if cls.ISSUE_KEY not in delete_tests_on_issue:
            for _, test_key in cls.tests_list:
                test_service.delete_test(test_key)
            delete_tests_on_issue.add(cls.ISSUE_KEY)

    yield

    # After each test suite
    if submit_tests:
        # Create test keys
        for name in cls.results:
            test_key = test_service.create_test(cls.__name__ + '_' + name,
                                                cls.ISSUE_KEY)
            cls.results[name]['testCaseKey'] = test_key
        test_cycle_items = [v for k, v in cls.results.items()]

        # Create test cycle
        test_service.create_test_cycle(cls.ISSUE_KEY + ' - ' + cls.__name__,
                                       cls.ISSUE_KEY, test_cycle_items)


@pytest.fixture()
def each_test_case(request):
    # Before each test case
    MAX_NAME_LENGTH = 255
    name = request._pyfuncitem.name
    if len(name) > MAX_NAME_LENGTH:
        name = name.substring(0, MAX_NAME_LENGTH)
    request.cls.results[name] = {'status': 'Pass'}
    yield

    # After each test case
    if request.node.test_outcome.failed:
        request.cls.results[name]['status'] = 'Fail'

