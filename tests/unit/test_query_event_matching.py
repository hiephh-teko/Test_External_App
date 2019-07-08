import logging
import pytest
from tests.jira import Jira
from external.query.event_matching_query import EventMatchingGoalQuery
from tests.mock_data.es_data import ESDataResultMatchingGoal

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

    
    # test in tracking site  - from_time="2019-06-25T13:18:22.000", end_time="2019-06-25T23:59:59.000"
    @pytest.mark.parametrize('field, value, from_time , end_time',
                            [
                                ('event.eventName','focusForm','2019-06-25T13:18:22.000','2019-06-25T23:59:59.000')
                            ])
    def test_query_contains_url_matching_correctly_tracking_site(self,field, value, from_time,end_time):
        expected_reusult = ESDataResultMatchingGoal("tracking-chat-tool-v2-*", from_time, end_time, field,value).get_len_contains_matching_data()

        result = len(EventMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("tracking-chat-tool-v2-*","contains",'eventName',value).get('hits').get('hits'))

        assert result == expected_reusult

    
    @pytest.mark.parametrize('field, value, from_time, end_time',
                            [
                                ('event.inputValue','.*Hiện tại bạn ở đâu.*','2019-05-31T03:22:22.000','2019-05-31T04:43:59.000')
                            ])
    def test_query_regex_url_matching_correctly_tracking_site(self,field, value, from_time , end_time):
        expected_reusult = ESDataResultMatchingGoal("tracking-chat-tool-v2-*", from_time, end_time, field,value).get_len_regex_matching_data()

        result = len(EventMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("tracking-chat-tool-v2-*","regex",'inputValue',value).get('hits').get('hits'))

        assert result == expected_reusult