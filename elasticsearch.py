
# #check ES is running 
import requests
res = requests.get('http://103.126.156.112:9200')
print(res.content)


# #connect to our cluster
# from elasticsearch import Elasticsearch
# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


#let's iterate over swapi people documents and index them
import json
# r = requests.get('http://localhost:9200') 
# i = 1
# while r.status_code == 200:
#     r = requests.get('http://swapi.co/api/people/'+ str(i))
#     es.index(index='sw', doc_type='people', id=i, body=json.loads(r.content))
#     i=i+1
 
# print(i)

# print(es.get(index='sw', doc_type='people', id=5))