from elasticsearch import Elasticsearch
import logging
import pytz
import requests
import json
import os
from dotenv import load_dotenv
from external.query.es_helper import ESHelper

class UrlMatchingGoalQuery(object):

    scroll_size = os.getenv('ELASTICSEARCH_SCROLL_SIZE')
    scroll_time = os.getenv('ELASTICSEARCH_SCROLL_TIME')
    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')

    def __init__(self, goal_table_data, from_time, end_time):
        self.goal_table_data = goal_table_data
        self.from_time = from_time
        self.end_time = end_time
        self.es_helper = ESHelper(self.scroll_time, self.scroll_size)
        self.es = self.es_helper.get_es_config()


    def get_query_contain_type_body(self, match_field, match_value, from_time, end_time):
        body = {
            "query": {
                "bool": {
                    "must": {
                        "regexp": {
                            match_field: {
                                "value": match_value
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

    # def get_query_regex_type_body(self, match_field, match_value, from_time, end_time):
    #     body = {
    #         "query": {
    #             "bool": {
    #                 "must": {
    #                     "regexp": {
    #                         match_field: {
    #                             "value": match_value
    #                         }
    #                     }
    #                 },
    #                 "filter": {
    #                     "range": {
    #                         "clientTime": {
    #                             "gte": from_time,
    #                             "lt": end_time
    #                         }
    #                     }
    #                 }
    #             }
    #         }
    #     }
    #     return body

    def get_hits_from_site_query(self, index, pattern_type, match_field, match_value):
      
        
        if str(pattern_type) == "contains":
            match_value = ".*%s.*"%(match_value)
        
        body = self.get_query_contain_type_body(
                match_field, match_value, self.from_time, self.end_time)

        # elif str(pattern_type) == "regex":
        #     body = self.get_query_regex_type_body(
        #         match_field, match_value, self.from_time, self.end_time)

        # Query Elasticsearch
        result_query = self.es_helper.get_results_execute_es(self.es,index,body)

        return result_query

    def enter_query(self):

        #get each goal for specific query
        for goal_data in self.goal_table_data:

            # get needed field, value  for query
            match_field = "event.href"
          
            match_value = str(goal_data.goal_pattern)
            # goal_field = str(f"event.{str(goal_data.goal_attribute)}")
       
            # get result of scroll by search
            data = self.get_hits_from_site_query(
                self.index_site_tracking, goal_data.pattern_type, match_field, match_value)


            # process scroll query
            self.es_helper.process_sroll_query(self.es,goal_data,data,self.from_time, self.end_time)

