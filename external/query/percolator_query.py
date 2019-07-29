from elasticsearch import Elasticsearch
import sys
from external.query.es_helper import ESHelper
import os
from datetime import datetime, timedelta

class ScrollQuery(object):
    def process_sroll_query(self, es, from_time, end_time):
        hits = []
        body = {
            "size":10000,
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
                }
        }

        data = es.search(index="tracking-chat-tool-v2-*",scroll='3m',size=10000,body=body)
        # Get the scroll ID
        sid = data.get('_scroll_id')

        scroll_size = len(data.get('hits').get('hits'))

        # Before scroll next, process current batch of hits
        tmp_hits = data.get('hits', {}).get('hits', [])
        for hit in tmp_hits:
            hits.append(hit)

        while (scroll_size > 0):
            data = es.scroll(scroll_id=sid, scroll='3m')

            # process current batch of hits
            tmp_hits = data.get('hits', {}).get('hits', [])
            for hit in tmp_hits:
                hits.append(hit)

            # update the scroll id
            sid = data.get('_scroll_id')

            # update scroll_size
            scroll_size = len(data.get('hits').get('hits'))
        
        return hits

class PercolatorQuery(object):
    
    index_site_tracking = "tracking-chat-tool-v2-*"

    def __init__(self, from_time, end_time):
        self.index = "test-index-percolate"
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()
        self.from_time = from_time
        self.end_time = end_time

        # print( self.es.indices.stats(index=self.index))
        # print(self.es.indices.stats(index="tracking-chat-tool-v2-2019.06.25"))

    def mappings_index(self, index):
        self.es.indices.delete(index=index,ignore=404)
        self.es.indices.delete(index="test-index-percolate-write",ignore=404)

        mapping = {
            "mappings": {
                "matching_query": {
                    "properties": {
                        "query": {
                            "type": "percolator"
                        },
                        "event": {
                            "properties": {
                                "eventName": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }   
                }
            }
        }
        # if not self.es.indices.exists(index=index):
        res = self.es.indices.create(index=index,body=mapping)
        print("create: ", res)

    def add_new_contains_percolator_query(self, index, field, value, id):
        body = {
            "query": {
                "term": {
                    field: {
                        "value": value
                    }
                }
            }
        }
        re = self.es.index(index=index,body=body,id=id)
    
    def add_new_regex_percolator_query(self, index, field, value, id):
        body = {
            "query": {
                "regexp": {
                    field: {
                        "value": value
                    }
                }
            }
        }
        re = self.es.index(index=index,body=body,id=id)
    
    def process_percolate_query(self,index_site_tracking, from_time, end_time, index):
        print("start query")
        body = {
            "size":10000,
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
                }
        }

        hits = self.es.search(index=index_site_tracking,body=body).get('hits').get('hits')

        print("start  process: ", datetime.now())
        count = 0
        for hit in hits:
            eventName = hit.get('_source').get('event').get('eventName')
            request_body = {
                "query": {
                    "percolate": {
                        "field": "query",
                        "document": {
                            "event.eventName" :  eventName
                        }
                    }
                }
            }   
            # print(request_body)
            res = self.es.search(index=index,body=request_body)
            # if not self.es.indices.exists(index="test-index-percolate-write"):
            #     self.es.indices.create(index="test-index-percolate-write")

            # print(res)
            if (len(res.get('hits').get('hits')) > 0):
                count+=1
                self.es.index(index="test-index-percolate-write",body={'event_log': hit})
                
            # print(res.get('hits').get('hits')[0].get('_id'))
            # break    
        print("end  process: ", datetime.now())
        print(count)
    

    def process_multi_percolate_query(self,index_site_tracking, from_time, end_time, index):

        hits = ScrollQuery().process_sroll_query(self.es,self.from_time,self.end_time)

        print("start  process: ", datetime.now())
        count = 0
     
        for hit in hits:
            eventName = hit.get('_source').get('event').get('eventName')
            request_body = {
                "query": {
                    "percolate": {
                        "field": "query",
                        "document": {
                            "event.eventName" :  eventName
                        }
                    }
                }
            }             

            res = self.es.search(index=index,body=request_body)
            if not self.es.indices.exists(index="test-index-percolate-write"):
                self.es.indices.create(index="test-index-percolate-write")

            # print(res)
            if (len(res.get('hits').get('hits')) > 0):
                count+=1
                self.es.index(index="test-index-percolate-write",body={'event_log': hit})   
            # print(res.get('hits').get('hits')[0].get('_id'))
            # break   
        print("end  process: ", datetime.now()) 
        print(count)    

    def enter(self):
        # self.mappings_index(self.index)

        # self.add_new_contains_percolator_query(self.index,"event.eventName","focusForm",1)
        # self.add_new_regex_percolator_query(self.index,"event.eventName",".*không còn hàng.*",2)
        # self.add_new_contains_percolator_query(self.index,"event.eventName","changeForm",3)
        self.es.indices.delete(index="test-index-percolate-write",ignore=404)

        self.process_multi_percolate_query(self.index_site_tracking, self.from_time, self.end_time, self.index)

        # self.process_percolate_query(self.index_site_tracking, self.from_time, self.end_time, self.index)

        
   


