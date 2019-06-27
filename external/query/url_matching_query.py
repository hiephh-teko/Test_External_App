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

    def __init__(self, data, from_time, end_time):
        self.data = data
        self.from_time = from_time
        self.end_time = end_time
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()


    def get_query_contain_type_body(self, match_field, match_value, goal_field, goal_value, from_time, end_time):
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                goal_field: {
                                    "value": goal_value
                                }
                            }
                        },
                        {
                            "term": {
                                match_field: {
                                    "value": match_value
                                }
                            }
                        }
                    ],
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

    def get_query_regex_type_body(self, match_field, match_value, goal_field, goal_value, from_time, end_time):
        body = {
            "query": {
                "bool": {
                    "must": [
                        {           
                            "term": {
                                match_field: {
                                    "value": match_value
                                }
                            }
                        },
                        {
                            "regexp": {
                                goal_field: {
                                    "value": goal_value
                                }
                            }
                        }
                    ],
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

    def get_hits_from_site_query(self, index, match_pattern_type, match_field, match_value, goal_field, goal_value):
        res = {
            '_scroll_id': None, 
            'hits': {
                'hits': []
            }
        }
        if str(match_pattern_type) == "contains":
            body = self.get_query_contain_type_body(
                match_field, match_value, goal_field, goal_value, self.from_time, self.end_time)
          

        elif str(match_pattern_type) == "regex":
            body = self.get_query_regex_type_body(
                match_field, match_value, goal_field, goal_value, self.from_time, self.end_time)

        # Query Elasticsearch
        result_query = self.es.search(
            index=index,
            scroll=self.scroll_time,
            size=self.scroll_size,
            body=body
        )

        return result_query

    def process_hits(self, stored_index, data, element_data):  
        hits = data.get('hits', {}).get('hits', [])

        print("goal_id: %d - goal_type: %s - app_id: %s - process_hits: %d" %(element_data.id,element_data.goal_type,element_data.app_id,len(hits)))

        for hit in hits:
            # get index body
            index_body = self.es_helper.get_matching_goal_log_index_body(hit, element_data, self.from_time, self.end_time)
            
            # write new doc
            self.es.index(index=stored_index, body=index_body)
            
    def enter_query(self):

        for element_data in self.data:

            # get needed field, value  for query
            match_field = str(f"event.{str(element_data.match_attribute)}")
            match_value = str(element_data.match_pattern)
            goal_field = str(f"event.{str(element_data.goal_attribute)}")
            goal_value = str(element_data.goal_pattern)
            stored_index = "<test-goal-%s-{now/d}>"%(element_data.app_id.lower())

            # get result of scroll by search
            data = self.get_hits_from_site_query(
                self.index_site_tracking, element_data.match_pattern_type, match_field, match_value, goal_field, goal_value)

            # Get the scroll ID
            if not data:
                data = {}
            sid = data.get('_scroll_id')
            scroll_size = len(data.get('hits', {}).get('hits', []))

            # Before scroll next, process current batch of hits
            self.process_hits(stored_index, data, element_data)

            while (scroll_size > 0):
                data = self.es.scroll(scroll_id=sid, scroll=self.scroll_time)

                # process current batch of hits
                self.process_hits(data.get('hits').get('hits'), element_data)

                # update the scroll id
                sid = data.get('_scroll_id')

                # update scroll_size
                scroll_size = len(data.get('hits').get('hits'))
