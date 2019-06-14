import json
import requests
from elasticsearch import Elasticsearch

class ElasticsearchConnect(object):

    es = Elasticsearch([{'host': '103.126.156.112', 'port': 9200}])


    def __init__(self, data): 
        self.data = data

    def query_contain_type_body(self, field, value):
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
        return body 
    
    def query_regex_type_body(self, field, value):
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
        return body

    def delete_index(self, index_name):
        res = self.es.indices.delete(index=index_name.lower())
        print("delete index:",res)


    def create_index(self, index_name):
        res = self.es.indices.create(index=index_name.lower())
        print("create index:",res)

    def open_connect(self):

        for element_data in self.data:

            # get needed field, value  for query
            field = str(f"event.{str(element_data.match_attribute)}")
            value = str(element_data.pattern)

            # get body query with CONTAINS & REGEX type
            if str(element_data.pattern_type) == "contains":
                body = self.query_contain_type_body(field,value)
            elif str(element_data.pattern_type) == "regex":
                body = self.query_regex_type_body(field,value)
            
            # Query Elasticsearch
            res2 = self.es.search(index='tracking-chat-tool-v2-*',body=body)
            self.create_index(element_data.app_id)
            # print("query", res2['hits']['total'])
            

            
        