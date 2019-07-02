import logging
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

class ESHelper(object):

    def __init__(self, scroll_time = '0m', scroll_size = 10000):
        self.scroll_size = scroll_size
        self.scroll_time = scroll_time

    def get_es_config(self):
        return Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'),
                         'port': os.getenv('ELASTICSEARCH_PORT')}])

    def get_matching_goal_log_index_body(self, hit, goal_data, from_time, end_time):
        return {
            'event_log': hit,
            'goal': {
                "id": goal_data.id,
                "name": goal_data.name,
                "description": goal_data.description,
                "match_attribute": goal_data.match_attribute,
                "match_pattern": goal_data.match_pattern,
                "match_pattern_type": goal_data.match_pattern_type,
                "case_sensitive": goal_data.case_sensitive,
                "allow_multiple": goal_data.allow_multiple,
                "revenue": goal_data.revenue,
                "conversion": goal_data.conversion,
                "goal_type": goal_data.goal_type,
                "goal_attribute": goal_data.goal_attribute,
                "goal_pattern": goal_data.goal_pattern,
                "deleted": goal_data.deleted,
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

    def get_results_execute_es(self, es, index,  body):
        result_query = es.search(
            index=index,
            scroll=self.scroll_time,
            size=self.scroll_size,
            body=body
        )
        return result_query


    def process_scroll_hits(self, es, data, goal_data, from_time, end_time):  
        hits = data.get('hits', {}).get('hits', [])
        print("goal_id: %d - goal_type: %s - app_id: %s - process_hits: %d" %(goal_data.id,goal_data.goal_type,goal_data.app_id,len(hits)))

        for hit in hits:
            # get index body
            index_body = self.get_matching_goal_log_index_body(hit, goal_data, from_time, end_time)
            
            # write new doc
            es.index(index="<test-goal-%s-{now/d}>"%(goal_data.app_id.lower()), body=index_body)
    
    def process_sroll_query(self, es, goal_data, data, from_time, end_time):
        # Get the scroll ID
        sid = data.get('_scroll_id')
        scroll_size = len(data.get('hits').get('hits'))

        # Before scroll next, process current batch of hits
        self.process_scroll_hits(es, data, goal_data, from_time, end_time)

        while (scroll_size > 0):
            data = es.scroll(scroll_id=sid, scroll=self.scroll_time)

            # process current batch of hits
            self.process_scroll_hits(es, data, goal_data, from_time, end_time)

            # update the scroll id
            sid = data.get('_scroll_id')

            # update scroll_size
            scroll_size = len(data.get('hits').get('hits'))
