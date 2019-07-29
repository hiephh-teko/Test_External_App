from external.query.es_helper import ESHelper
import re

class ESData(object):
    
    def __init__(self, index, from_time="2019-06-25T13:18:22.000", end_time="2019-06-25T23:59:59.000"):
        self.es_helper = ESHelper()
        self.es = self.es_helper.get_es_config()

        self.index = index
        self.from_time = from_time
        self.end_time = end_time

    def get_data_from_es_index(self):
        body = {
            "size": 10000,
            "query": {
                "range": {
                    "clientTime": {
                        "gte": self.from_time,
                        "lt": self.end_time
                    }
                }
            }
        }

        hits = self.es.search(index=self.index,body=body).get("hits").get("hits")
        # print(len(hits))
        
        return hits


class ESDataResultMatchingGoal(object):

    def __init__(self, index, from_time, end_time, match_field, match_value, goal_field="", goal_value=""):
        self.hits = ESData(index, from_time, end_time).get_data_from_es_index()

        self.match_field = match_field
        self.match_value = match_value
        self.goal_field = goal_field
        self.goal_value = goal_value

    def check_contains_matching(self, event, field, value):
        field_data = event.get(field,"")
        if field_data is value:
            return True
        else:
            return False
    
    def check_regex_matching(self, event, field, value):
        field_data = event.get(field,"")
        res_matching = re.search(value,field_data)
        if (res_matching):
            print(field_data,value)

            return True
        else:
            return False

    def get_len_contains_matching_data(self):
        count = 0
        for hit in self.hits:
            event = hit.get("_source").get("event")
            if self.check_contains_matching(event,self.match_field,self.match_value):
                if self.goal_field is "":
                    count+=1
                else:
                    if self.check_contains_matching(event,self.goal_field,self.goal_value):
                        count+=1
        
        return count
                
    def get_len_regex_matching_data(self):
        count = 0
        for hit in self.hits:
            event = hit.get("_source").get("event")


            if (self.check_regex_matching(event,self.match_field,self.match_value)):
                if self.goal_field is "":
                    count+=1
                else:
                    if (self.check_regex_matching(event,self.goal_field,self.goal_value)):
                        count+=1
        
        return count








