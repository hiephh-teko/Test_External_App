import logging
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

class ESHelper(object):


    def __init__(self, scroll_time = '2m', scroll_size = 10000):
        self.scroll_size = scroll_size
        self.scroll_time = scroll_time
        self.index_write_matching_goal = os.getenv('ELASTICSEARCH_INDEX_WRITE_MATCHING_GOAL')

    def get_es_config(self):
        return Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'),
                         'port': os.getenv('ELASTICSEARCH_PORT')}])

    def get_matching_goal_log_index_body(self, hit, goal_data, from_time, end_time):
        return {
            'event_log': hit,
            'goal': {
                "goal_id": goal_data.goal_id,
                "app_id": goal_data.app_id,
                "goal_name": goal_data.goal_name,
                "description": goal_data.description,
                "goal_type": goal_data.goal_type,
                "goal_pattern": goal_data.goal_pattern,
                "pattern_type": goal_data.pattern_type,
                "threshold": goal_data.threshold,
                "case_sensitive": goal_data.case_sensitive,
                "allow_multiple": goal_data.allow_multiple,
                "deleted": goal_data.deleted,
                "activeness": goal_data.activeness,
                "start_time": from_time,
                "end_time": end_time
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
        print("start goal_id: %d - goal_type: %s - process_hits: %d" %(goal_data.goal_id,goal_data.goal_type,len(hits)))

        count = 0
        for hit in hits:
            # get index body
            index_body = self.get_matching_goal_log_index_body(hit, goal_data, from_time, end_time)
            
            # write new doc
            es.index(index="<%s-%s-{now/d}>"%(self.index_write_matching_goal,goal_data.app_id.lower()), body=index_body)
            count += 1
        print("write to index matching goal %s%d"%(goal_data.goal_id,count))

        print("endgoal_type: %s " %(goal_data.goal_type))

    
    def process_sroll_query(self, es, goal_data, data, from_time, end_time):
        # Get the scroll ID
        sid = data.get('_scroll_id')
        
        scroll_size = len(data.get('hits').get('hits'))

        # Before scroll next, process current batch of hits
        self.process_scroll_hits(es, data, goal_data, from_time, end_time)

        while (scroll_size > 0):
            print("start scroll: ")
            data = es.scroll(scroll_id=sid, scroll=self.scroll_time)
            print("end scroll: ", data)
            # process current batch of hits
            self.process_scroll_hits(es, data, goal_data, from_time, end_time)

            # clear scroll id
            clear_es = es.clear_scroll(scroll_id=sid)
            print("clear :", clear_es)

            # update the scroll id
            sid = data.get('_scroll_id')
            print("sid: ", sid)

            # update scroll_size
            scroll_size = len(data.get('hits').get('hits'))

