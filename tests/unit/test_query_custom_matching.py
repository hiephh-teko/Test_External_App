import logging
import pytest
from tests.jira import Jira
from external.query.custom_matching_query import CustomMatchingQuery

class TestQueryCustomMatching(Jira):
    ISSUE_KEY = 'TAP-76'


    @pytest.mark.parametrize(' field, value, from_time , end_time, expected_reusult',
                            [
                                ('event.eventName.keyword','changeForm','2019-06-26T00:00:00.000','2019-06-26T23:59:59.000',6),
                                ('event.eventName.keyword','changeForm','2019-06-25T00:00:00.000','2019-06-25T23:59:59.000',4)
                            ])
    def test_query_contains_matching_correctly(self, field, value, from_time , end_time, expected_reusult):
        result = len(CustomMatchingQuery(None,from_time,end_time).get_hits_from_site_query("mock-test-goal",field, value).get('hits').get('hits'))

        assert result == expected_reusult