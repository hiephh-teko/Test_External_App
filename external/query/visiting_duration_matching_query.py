from elasticsearch import Elasticsearch
import logging
import pytz
import requests
import json
import os
from dotenv import load_dotenv
from external.query.es_helper import ESHelper

class VisitingDurationMatching(object):

    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')

    def __init__(self, goal_table_data, from_time, end_time):
        self.goal_table_data = goal_table_data
        self.from_time = from_time
        self.end_time = end_time
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()

    def get_query_body(self, value, from_time, end_time):
        body= {
            "size": 0, 
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "clientTime": {
                                "gte": from_time,
                                "lt": end_time
                            }
                        }
                    }
                }
            }, 
            "aggs": {
                "visit_elapse_time": {
                    "terms": {
                        "field": "session.id",
                        "size": 2148,
                        "show_term_doc_count_error": 'true'
                    },
                    "aggs": {
                        "session_start": {
                            "min": {
                                "field": "session.createdAt"
                            }
                        },
                        "session_end": {
                            "max": {
                                "field": "session.lastActiveAt"
                            }
                        },
                        "session_length": {
                            "bucket_script": {
                                "buckets_path": {
                                    "endTime": "session_end",
                                    "startTime": "session_start"
                                },
                                "script": "params.endTime - params.startTime"
                            }
                        },
                        "duration_matching":{
                            "bucket_selector": {
                                "buckets_path": {
                                    "sessionLength": "session_length"
                                },
                                "script": "params.sessionLength > %s"%(value)
                            }
                        },
                        "session_hit":{
                            "top_hits": {
                                "size": 1
                            }
                        }
                    }
                }
            }
        }
        return body

    def get_hits_from_site_query(self, value, index):
        body = self.get_query_body(value,self.from_time,self.end_time)

        # Query Elasticsearch
        result_query = self.es.search(index=index,body=body)

        return result_query

    def enter_query(self):

        number_of_session = self.es_helper.get_number_of_session(self.es,self.index_site_tracking,self.from_time, self.end_time)
        print("number_of_session:", number_of_session)
        
        #get each goal for specific query
        for goal_data in self.goal_table_data:

            #get needed field, value  for query
            value = str(goal_data.match_pattern)

            #get result of query matching goal
            data = self.get_hits_from_site_query(value,self.index_site_tracking)
            
            # print(data.get('aggregations').get('visit_elapse_time').get('buckets')[0])
            #process 

             



