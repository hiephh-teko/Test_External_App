import logging
import pytest
from tests.jira import Jira
from external.query.event_matching_query import EventMatchingGoalQuery

class TestQueryEventMatching(Jira):
    ISSUE_KEY = 'TAP-75'

    # test in date 20/6, 5/6 
    @pytest.mark.parametrize('field, value, from_time , end_time, expected_reusult',
                            [
                                ('event.eventName.keyword','focusForm','2019-06-20T00:00:00.000','2019-06-20T23:59:59.000',7),
                                ('event.eventName.keyword','focusForm','2019-06-05T00:00:00.000','2019-06-05T23:59:59.000',12)
                            ])
    def test_query_contains_url_matching_correctly(self,field, value, from_time , end_time, expected_reusult):
        result = len(EventMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("mock-test-goal","contains",field,value).get('hits').get('hits'))

        assert result == expected_reusult


    #test in date 1/6-5/6
    @pytest.mark.parametrize('field, value, from_time , end_time, expected_reusult',
                            [
                                ('event.inputValue.keyword','.*không còn hàng.*','2019-06-01T00:00:00.000','2019-06-05T23:59:59.000',4)
                            ])
    def test_query_regex_url_matching_correctly(self,field, value, from_time , end_time, expected_reusult):
        result = len(EventMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("mock-test-goal","regex",field,value).get('hits').get('hits'))

        assert result == expected_reusult