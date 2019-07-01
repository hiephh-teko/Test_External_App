import logging
import pytest
import os
from tests.jira import Jira
from external.query.url_matching_query import UrlMatchingGoalQuery
from tests.data.input.mock_test_sql_table import SqlMockTable
from external.query.es_helper import ESHelper


class TestQueryEventMatching(Jira):
    ISSUE_KEY = 'TAP-72'

    
    @pytest.mark.parametrize(' match_field, match_value, goal_field, goal_value, from_time , end_time, expected_reusult',
                            [
                                ('event.eventName.keyword','pageLoad','event.href.keyword','https://chat-v2.teko.vn/','2019-06-25T00:00:00.000','2019-06-25T23:59:59.000',14),
                                ('event.eventName.keyword','pageLoad','event.href.keyword','https://chat-v2.teko.vn/','2019-06-24T00:00:00.000','2019-06-24T23:59:59.000',4)
                            ])
    def test_query_contains_matching_correctly(self,match_field, match_value, goal_field, goal_value, from_time , end_time, expected_reusult):
        result = len(UrlMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("mock-test-goal","contains", match_field, match_value, goal_field, goal_value).get('hits').get('hits'))

        assert result == expected_reusult


    @pytest.mark.parametrize(' match_field, match_value, goal_field, goal_value, from_time , end_time, expected_reusult',
                            [
                                ('event.eventName.keyword','pageLoad','event.href.keyword','https://chat-v2.teko.vn/stocks.*','2019-06-25T00:00:00.000','2019-06-25T23:59:59.000',3),
                                ('event.eventName.keyword','pageLoad','event.href.keyword','https://chat-v2.teko.vn/stocks.*','2019-06-24T00:00:00.000','2019-06-24T23:59:59.000',9)
                            ])
    def test_query_regex_matching_correctly(self,match_field, match_value, goal_field, goal_value, from_time , end_time, expected_reusult):
        result = len(UrlMatchingGoalQuery(None,from_time,end_time).get_hits_from_site_query("mock-test-goal","regex", match_field, match_value, goal_field, goal_value).get('hits').get('hits'))

        assert result == expected_reusult





    # TEST - CHECK ABILITY WRITE DOC IN ES
    # mock_table = SqlMockTable()
    # index_site_tracking = "mock-test-goal"
    # es_helper = ESHelper('1m',3)
    # es = es_helper.get_es_config()
    # index_write_doc = "mock-test-write-doc"


    # @pytest.mark.parametrize('from_time, end_time, expected_reusult',
    #                         [
    #                             ('2019-06-24T00:00:00.000','2019-06-24T23:59:59.000',9)
    #                         ])
    # def test_write_goal_document_es_correctly(self, from_time , end_time, expected_reusult):

       
    #     goal_data = self.mock_table.get_regex_url_matching()
    #     url_matching_goal_query = UrlMatchingGoalQuery(None,from_time,end_time)

    #     if self.es.indices.exists(index=self.index_write_doc):
    #         print("exists")
    #         self.es.indices.delete(index=self.index_write_doc)

    #     data = url_matching_goal_query.get_hits_from_site_query(
    #         self.index_site_tracking, goal_data.match_pattern_type, 
    #         goal_data.match_attribute, goal_data.match_pattern, 
    #         goal_data.goal_attribute, goal_data.goal_pattern)

    #     url_matching_goal_query.process_hits(self.index_write_doc,data,goal_data)

    #     yield
            
    #     res = self.es.search(index='mock-test-write-doc',body=self.es_helper.get_index_body_query_filter_range_time(from_time, end_time))
    #     print(self.es_helper.get_index_body_query_filter_range_time(from_time, end_time))
    #     print(res)

    #         # 

    #     assert res['hits']['total'] == expected_reusult

        
