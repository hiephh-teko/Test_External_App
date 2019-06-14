import json
import requests
from elasticsearch import Elasticsearch

class ElasticsearchConnect(object):

    def __init__(self, data): 
        self.data = data

    def query_contain_type(self, es, field, value):
        print(field,value)
        body = {
            "size": 0, 
            "query":{
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            field : value
                        }
                    }
                }
            }      
        }
        res2 = es.search(index='tracking-chat-tool-v2-*',body=body)
        # print(res2)
        print(res2['hits']['total'])
    
    def query_regex_type(self, es, field, value):
        print(field,value)
        body = {
            "size": 0, 
            "query": {
                "bool": {
                    "must": [
                        {
                            "regexp": {
                                field:{
                                    "value": value
                                }
                            }
                        }
                    ]
                }
            }   
        }
        print(body)
        res2 = es.search(index='tracking-chat-tool-v2-*',body=body)
        # print(res2)
        # print(res2['hits']['total'])

    def open_connect(self):
        es = Elasticsearch([{'host': '103.126.156.112', 'port': 9200}])

        for element_data in self.data:

            field = str(f"event.{str(element_data.match_attribute)}")
            value = str(element_data.pattern)

            if str(element_data.pattern_type) == "contains":
                self.query_contain_type(es,field,value)
            elif str(element_data.pattern_type) == "regex":
                # print(field,value)
                self.query_regex_type(es,type,field)
            

            
        