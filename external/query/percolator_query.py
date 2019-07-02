from elasticsearch import Elasticsearch
import sys
from external.query.es_helper import ESHelper
import os

class PercolatorQuery(object):
    
    index_site_tracking = os.getenv('ELASTICSEARCH_INDEX_SITE_TRACKING')

    def __init__(self):
        self.index = "test-index-percolate"
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()

    def mappings_index(self, index):
        self.es.indices.delete(index=index)

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
                                },
                                "pageName": {
                                    "type": "keyword"
                                },
                                "href": {
                                    "type": "keyword"
                                },
                                "eventType": {
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

    def add_new_percolator_query(self, index, field, value):
        body = {
            "query": {
                "term": {
                    field: {
                        "value": value
                    }
                }
            }
        }

        re = self.es.index(index=index,body=body)
        print("add: ", re)
    
    def process_percolate_query(self,index_site_tracking, index):
        body = {
            "size": 10000,
            "query": {
                "match_all": {}
            }
        }

        hits = self.es.search(index=index_site_tracking,body=body).get('hits').get('hits')
        print("run")
        for hit in hits:
            # print(hit)
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
            # print(res.get('hits').get('hits')[0].get('_id'))
            # break    
    
    def enter(self):
        self.mappings_index(self.index)
        self.add_new_percolator_query(self.index,"event.eventName","pageUnload")
        self.add_new_percolator_query(self.index,"event.eventName","pageLoad")
        self.add_new_percolator_query(self.index,"event.eventName","HeartBeatEvent")

        self.process_percolate_query(self.index_site_tracking,self.index)




