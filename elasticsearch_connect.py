import json
import requests
import datetime
from elasticsearch import Elasticsearch

class ElasticsearchConnect(object):

    es = Elasticsearch([{'host': '103.126.156.112', 'port': 9200}])

    def __init__(self, data): 
        self.data = data

    def query_contain_type_body(self, field, value):
        body = {
            "size": 0,
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
                                "gte": "now-1d",
                                "lt": "now"
                            }
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
                    "must": {
                        "regexp": {
                            field:{
                                "value": value
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "clientTime": {
                                "gte": "now-1d",
                                "lt": "now"
                            }
                        }
                    }
                }
            }   
        }
        return body

    def delete_index(self, index_name):
        res = self.es.delete(index=index_name.lower())
        print("delete index:",res)

    def create_index(self, index_name):
        print("into create index function")
        request_body = {
            "settings" : {
                "number_of_shards": 3,
                "number_of_replicas": 1
            },
            "mappings": {
                "goal": {
                    "properties": {
                        "id": { "type": "long" },
                        "name": { "type": "keyword" },
                        "description": { "type": "text" },
                        "match_attribute": { "type": "keyword" },
                        "pattern": { "type": "keyword" },
                        "pattern_type": { "type": "keyword" },
                        "case_sensitive": { "type": "boolean" },
                        "allow_multiple": { "type": "boolean" },
                        "revenue": { "type": "boolean" },
                        "conversion": { "type": "boolean" },
                        "app_id": { "type": "keyword" },
                        "goal_type": { "type": "keyword" },
                        "goal_pattern": { "type": "keyword" },
                        "deleted": { "type": "boolean" },
                        "time": { "type": "date" },
                        "value" : {"type" : "long"}
                    }
                }
            }
        }
        res = self.es.index(index=index_name.lower(),body=request_body)
    #     print("create index:",res)

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
            res2 = self.es.search(index="tracking-chat-tool-v2-*",body=body)
            print("query", res2["hits"]["total"])

            #ádfkjklasdfhjklfhasdkljfasdhklsdfjahjklsdfh self.create_index(element_data.app_id)
            index_body={
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
                "app_id": element_data.app_id,
                "goal_type": element_data.goal_type,
                "goal_pattern": element_data.goal_pattern,
                "deleted": element_data.deleted,
                "time": datetime.datetime.now(),
                "value": res2["hits"]["total"]
            }
            
            res3 = self.es.index(index="<goal-{now/d}>",body=index_body)
            print("add new document:", res3)
            # self.delete_index(element_data.app_id)
            

            
        