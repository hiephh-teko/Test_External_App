import json
import requests
from elasticsearch import Elasticsearch

class ElasticsearchConnect(object):

    def __init__(self, data): 
        self.data = data

    def open_connect(self):
        res = requests.get('http://103.126.156.112:9200')
        print(res.status_code)
        es = Elasticsearch([{'host': '103.126.156.112', 'port': 9200}])
        
        eventname_text = f"event.{str(self.data[0].match_attribute)}".rstrip()
        pattern_text = str(self.data[0].pattern)
        body = {
            "size": 0, 
            "query":{
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            eventname_text : pattern_text
                        }
                    }
                }
            }     
            
        }
        
        res2 = es.search(index='tracking-chat-tool-v2-*',body=body)
        print(res2)
        print(res2['hits']['total'])
        


# #connect to our cluster
# from elasticsearch import Elasticsearch
# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


#let's iterate over swapi people documents and index them

# r = requests.get('http://localhost:9200') 
# i = 1
# while r.status_code == 200:
#     r = requests.get('http://swapi.co/api/people/'+ str(i))
#     es.index(index='sw', doc_type='people', id=i, body=json.loads(r.content))
#     i=i+1
 
# print(i)

# print(es.get(index='sw', doc_type='people', id=5))