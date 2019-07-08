from external.query.es_helper import ESHelper

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

    def get_len_matching_data(self):
        count = 0
        for hit in self.hits:
            event = hit.get("_source").get("event")
            match_field_data = event.get(self.match_field,"")
            if match_field_data is self.match_value:
                if self.goal_field is "":
                    count+=1
                else:
                    goal_field_data = hit.get(self.goal_field,"")
                    if goal_field_data is self.goal_value:
                        count+=1
        
        return count
                






