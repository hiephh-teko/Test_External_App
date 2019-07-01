# coding=utf-8
import logging
import os
from operator import itemgetter

import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class JiraService:

    def __init__(self):
        self.project_key = os.getenv('JIRA_PROJECT_KEY')
        self.auth_string = (os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD'))
        self.base_url = '{}/rest/atm/1.0'.format(os.getenv('JIRA_URL'))

    def __now(self):
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    def get_tests_in_issue(self, issue_key):
        params = {
            'query':
                'projectKey = "%s" AND issueKeys IN (%s)' %
                (self.project_key, issue_key)
        }
        response = requests.get(url=self.base_url + '/testcase/search',
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
        response = requests.post(url=self.base_url + '/testcase',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test return with error status code',
                            response.status_code)

        test_key = response.json()['key']
        return test_key

    def delete_test(self, test_key):
        response = requests.delete(url=self.base_url + '/testcase/' + test_key,
                                   auth=self.auth_string)
        if response.status_code != 204:
            raise Exception('Delete test return with error status code',
                            response.status_code)

    def create_test_cycle(self, name, issue_key, items):

        json = {
            'name': name,
            'projectKey': self.project_key,
            'issueKey': issue_key,
            'plannedStartDate': self.__now(),
            'plannedEndDate': self.__now(),
            'items': items
        }
        response = requests.post(url=self.base_url + '/testrun',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test cycle return with error status code',
                            response.status_code)
