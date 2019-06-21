from elasticsearch import Elasticsearch
import pytz
import requests
import json
import os
from dotenv import load_dotenv
_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(_DOT_ENV_PATH)


class UrlMatchingGoalQuery(object):

    es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'),
                         'port': os.getenv('ELASTICSEARCH_PORT')}])
    scroll_size = os.getenv('ELASTICSEARCH_SCROLL_SIZE')
    scroll_time = os.getenv('ELASTICSEARCH_SCROLL_TIME')
    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')

    def __init__(self, data, from_time, end_time):
        self.data = data
        self.from_time = from_time
        self.end_time = end_time

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

    def get_hits_from_site_query(self, index, pattern_type, field, value):

        if str(pattern_type) == "contains":
            body = self.get_query_contain_type_body(
                field, value, self.from_time, self.end_time)

        elif str(pattern_type) == "regex":
            body = self.get_query_regex_type_body(
                field, value, self.from_time, self.end_time)

        # Query Elasticsearch
        result_query = self.es.search(
            index=index,
            scroll=self.scroll_time,
            size=self.scroll_size,
            body=body
        )

        return result_query

    def get_matching_goal_log_index_body(self, hit, element_data):
        return {
            'event_log':
                hit,
            'goal': {
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
        print("process_hits:", len(hits))
        # count = 0
        # print("hits1", hits[0])
        for hit in hits:
            # get index body
            index_body = self.get_matching_goal_log_index_body(
                hit, element_data)
            
            # write new doc
            self.es.index(index="<test-goal-{now/d}>", body=index_body)

    def enter_query(self):

        for element_data in self.data:
            print("app_id: %s - idGoal: %s" %(element_data.app_id,element_data.id))
            # get needed field, value  for query
            field = str(f"event.{str(element_data.match_attribute)}")
            value = str(element_data.pattern)

            # get result of scroll by search
            data = self.get_hits_from_site_query(
                self.index_site_tracking, element_data.pattern_type, field, value)

            # Get the scroll ID
            sid = data.get('_scroll_id')
            scroll_size = len(data.get('hits').get('hits'))

            # Before scroll next, process current batch of hits
            self.process_hits(data.get('hits').get('hits'), element_data)

            while (scroll_size > 0):
                data = self.es.scroll(scroll_id=sid, scroll=self.scroll_time)

                # process current batch of hits
                self.process_hits(data.get('hits').get('hits'), element_data)

                # update the scroll id
                sid = data.get('_scroll_id')

                # update scroll_size
                scroll_size = len(data.get('hits').get('hits'))
