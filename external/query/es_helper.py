import logging
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

class ESHelper(object):

    scroll_time = os.getenv('ELASTICSEARCH_SCROLL_TIME')


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


    def process_scroll_hits(self, es, data, element_data, from_time, end_time):  
        hits = data.get('hits', {}).get('hits', [])
        print("goal_id: %d - goal_type: %s - app_id: %s - process_hits: %d" %(element_data.id,element_data.goal_type,element_data.app_id,len(hits)))

        for hit in hits:
            # get index body
            index_body = self.get_matching_goal_log_index_body(hit, element_data, from_time, end_time)
            
            # write new doc
            es.index(index="<test-goal-%s-{now/d}>"%(element_data.app_id.lower()), body=index_body)
    
    def process_sroll_query(self, es, element_data, data, from_time, end_time):
        # Get the scroll ID
        sid = data.get('_scroll_id')
        scroll_size = len(data.get('hits').get('hits'))

        # Before scroll next, process current batch of hits
        self.process_scroll_hits(es, data, element_data, from_time, end_time)

        while (scroll_size > 0):
            data = es.scroll(scroll_id=sid, scroll=self.scroll_time)

            # process current batch of hits
            self.process_scroll_hits(es, data, element_data, from_time, end_time)

            # update the scroll id
            sid = data.get('_scroll_id')

            # update scroll_size
            scroll_size = len(data.get('hits').get('hits'))
