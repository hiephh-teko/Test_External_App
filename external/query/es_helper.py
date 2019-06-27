import logging
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

class ESHelper(object):


    def get_es_config(self):
        return Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'),
                         'port': os.getenv('ELASTICSEARCH_PORT')}])

    def get_matching_goal_log_index_body(self, hit, element_data, from_time, end_time):
        return {
            'event_log': hit,
            'goal': {
                "id": element_data.id,
                "name": element_data.name,
                "description": element_data.description,
                "match_attribute": element_data.match_attribute,
                "match_pattern": element_data.match_pattern,
                "match_pattern_type": element_data.match_pattern_type,
                "case_sensitive": element_data.case_sensitive,
                "allow_multiple": element_data.allow_multiple,
                "revenue": element_data.revenue,
                "conversion": element_data.conversion,
                "goal_type": element_data.goal_type,
                "goal_attribute": element_data.goal_attribute,
                "goal_pattern": element_data.goal_pattern,
                "deleted": element_data.deleted,
                "start_time": from_time,
                "end_time": end_time
            }
        }

    def get_index_body_query_filter_range_time(self, from_time, end_time):
        return{
                "query": {
                    "range": {
                        "event_log._source.clientTime": {
                            "gte": from_time,
                            "lt": end_time
                        }
                    }
                }
            }    
