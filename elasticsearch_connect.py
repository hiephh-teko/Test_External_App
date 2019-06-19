import json
import requests
from datetime import datetime, timedelta
import pytz
from elasticsearch import Elasticsearch

class ElasticsearchConnect(object):

    es = Elasticsearch([{'host': '103.126.156.112', 'port': 9200}])
    hours_query = 10000
    scroll_size = 10000
    scroll_time = '2m'
    from_time = (datetime.now() - timedelta(hours = hours_query)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    end_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 
    # print(from_time, end_time)

    def __init__(self, data): 
        self.data = data

    def query_contain_type_body(self, field, value, from_time, end_time):
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
                                "gte": from_time ,
                                "lt": end_time
                            }
                        }
                    }
                }
            }  
        }
        return body 
    
    def query_regex_type_body(self, field, value, from_time, end_time):
        body = {
            "query": { 
                "bool": {
                    "must": {
                        "regexp": {
                            field:{
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

    def get_hits_from_site_query(self, pattern_type, field, value):

        if str(pattern_type) == "contains": 
            body = self.query_contain_type_body(field, value, self.from_time, self.end_time)

        elif str(pattern_type) == "regex":
            body = self.query_regex_type_body(field,value, self.from_time, self.end_time)

        # Query Elasticsearch
        result_query = self.es.search(
                                        index="tracking-chat-tool-v2-*",
                                        scroll=self.scroll_time,
                                        size=self.scroll_size,
                                        body=body
                                    )

        return result_query
    

    def get_matching_goal_log_index_body(self, hit, element_data):
        return {
            'event_log':
                hit
            ,
            'goal' : {
                "id": element_data.id,
                "name": element_data.name,
                "description": element_data.description,
                "match_attribute": element_data.match_attribute,
                "pattern": element_data.pattern,
                "pattern_type": element_data.pattern_type,
                "case_sensitive": element_data.case_sensitive,
                "allow_multiple": element_data.allow_multiple,
                "revenue": element_data.revenue,
                "conversion": element_data.conversion,
                "goal_type": element_data.goal_type,
                "goal_pattern": element_data.goal_pattern,
                "deleted": element_data.deleted,
                "start_time": self.from_time,
                "end_time": self.end_time
            }
        }

    def process_hits(self, hits, element_data):
        print(len(hits))
        for hit in hits:
                    
            index_body = self.get_matching_goal_log_index_body(hit, element_data)

            result_add_new_doc = self.es.index(index="<goal-{now/d}>",body=index_body)
            # print("add new document:", result_add_new_doc)

    def enter_query(self):

        total_hits = 0

        for element_data in self.data:

            # get needed field, value  for query
            field = str(f"event.{str(element_data.match_attribute)}")
            value = str(element_data.pattern)
            
            # get result of scroll by search
            data = self.get_hits_from_site_query(element_data.pattern_type, field, value)
            
            # Get the scroll ID
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])

            # Before scroll next, process current batch of hits
            self.process_hits(data['hits']['hits'], element_data)

            while (scroll_size > 0):
                data = self.es.scroll(scroll_id=sid,scroll=self.scroll_time)

                # process current batch of hits
                self.process_hits(data['hits']['hits'], element_data)

                #update the scroll id
                sid = data['_scroll_id']

                #update scroll_size
                scroll_size = len(data['hits']['hits'])

     
            