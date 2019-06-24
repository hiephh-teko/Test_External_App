# coding=utf-8
import logging

import pytest

from tests.jira.services import JiraService

_logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('update_test_result', 'jira_test_suite')
class Jira:
    pass
