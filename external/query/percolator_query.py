from elasticsearch import Elasticsearch
import sys
from external.query.es_helper import ESHelper
import os

class PercolatorQuery(object):
    
    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')

    def __init__(self, from_time, end_time):
        self.index = "test-index-percolate"
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()
        self.from_time = from_time
        self.end_time = end_time

    def mappings_index(self, index):
        # self.es.indices.delete(index=index)

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
        if not self.es.indices.exists(index=index):
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
                "wildcard": {
                    field: value
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
        print("run  hit")
        count = 0
        for hit in hits:
            request_body = {
                "query": {
                    "percolate": {
                        "field": "query",
                        "document": {
                            "event.eventName" :  hit.get('_source').get('event').get('eventName')
                        }
                    }
                }
            }   
            # print(request_body)
            res = self.es.search(index=index,body=request_body)
            if not self.es.indices.exists(index="test-index-percolate-write"):
                self.es.indices.create(index="test-index-percolate-write")
            if (len(res.get('hits').get('hits')) > 0):
                self.es.index(index="test-index-percolate-write",body={'event_log': hit})
                count+=1
            # print(res.get('hits').get('hits')[0].get('_id'))
            # break    
        print(count)
    
    def enter(self):
        self.mappings_index(self.index)

        self.add_new_contains_percolator_query(self.index,"event.eventName","focusForm",1)
        self.add_new_regex_percolator_query(self.index,"event.eventName","*không còn hàng*",2)
        self.add_new_contains_percolator_query(self.index,"event.eventName","changeForm",3)

        self.process_percolate_query(self.index_site_tracking, self.from_time, self.end_time, self.index)




