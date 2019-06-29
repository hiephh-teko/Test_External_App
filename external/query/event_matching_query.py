from elasticsearch import Elasticsearch
import logging
import pytz
import requests
import json
import os
from dotenv import load_dotenv
from external.query.es_helper import ESHelper

class EventMatchingGoalQuery(object):

    scroll_size = os.getenv('ELASTICSEARCH_SCROLL_SIZE')
    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')
    scroll_time = os.getenv('ELASTICSEARCH_SCROLL_TIME')

    def __init__(self, goal_table_data, from_time, end_time):
        self.goal_table_data = goal_table_data
        self.from_time = from_time
        self.end_time = end_time
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()

    def get_query_contain_type_body(self, field, value, from_time, end_time):
        body = {
            "query": {
                "bool": {
                    "must": {
                        "term": {
                            field: {
                                "value": value
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "clientTime": {
                                "gte": from_time,
                                "lt": end_time
                            }
                        }
                    }
                }
            }
        }
        return body

    def get_query_regex_type_body(self, field, value, from_time, end_time):
        body = {
            "query": {
                "bool": {
                    "must": {
                        "regexp": {
                            field: {
                                "value": value
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "clientTime": {
                                "gte": from_time,
                                "lt": end_time
                            }
                        }
                    }
                }
            }
        }
        return body

    def get_hits_from_site_query(self, index, match_pattern_type, field, value):

        if str(match_pattern_type) == "contains":
            body = self.get_query_contain_type_body(
                field, value, self.from_time, self.end_time)

        elif str(match_pattern_type) == "regex":
            body = self.get_query_regex_type_body(
                field, value, self.from_time, self.end_time)

        # Query Elasticsearch
        result_query = self.es_helper.get_results_execute_es(self.es,index,self.scroll_time,self.scroll_size,body)

        return result_query


    def enter_query(self):

        for goal_data in self.goal_table_data:
            # get needed field, value  for query
            field = str(f"event.{str(goal_data.match_attribute)}")
            value = str(goal_data.match_pattern)

            # get result of scroll by search
            data = self.get_hits_from_site_query(
                self.index_site_tracking, goal_data.match_pattern_type, field, value)

            # process scroll query
            self.es_helper.process_sroll_query(self.es,goal_data,data,self.from_time, self.end_time)
