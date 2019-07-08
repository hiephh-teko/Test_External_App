import threading
import os
from datetime import datetime, timedelta
from external.query.url_matching_query import UrlMatchingGoalQuery
from external.query.event_matching_query import EventMatchingGoalQuery
from external.query.custom_matching_query import CustomMatchingQuery
from external.query.percolator_query import PercolatorQuery
from external.database_init import DatabaseInit

class BaseThread(threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    
    def run(self):
        print("starting thread %s"%(self.name))

class ThreadQuery(object):

    def enter_thread(self):
        hours_query = os.getenv('ELASTICSEARCH_HOURS_QUERY')

        from_time = (datetime.now() - timedelta(minutes = int(hours_query))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        end_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 
        # from_time = "2019-06-25T13:18:22.000"
        # end_time = "2019-06-25T23:59:59.000"
        print("run from %s to %s"%(from_time,end_time))

        event_matching_data = DatabaseInit().get_data_event_matching()  
        event_matching_thread = threading.Thread(target=EventMatchingGoalQuery(event_matching_data,from_time,end_time).enter_query,name="event_matching_thread")

        url_matching_data = DatabaseInit().get_data_url_matching()
        url_matching_thread = threading.Thread(target=UrlMatchingGoalQuery(url_matching_data,from_time,end_time).enter_query,name="url_matching_thread")

        custom_matching_data = DatabaseInit().get_data_custom_matching()
        custom_matching_thread = threading.Thread(target=CustomMatchingQuery(custom_matching_data,from_time, end_time).enter_query,name="custom_matching_thread")

        custom_matching_thread.start()
        event_matching_thread.start()
        url_matching_thread.start()
 
        event_matching_thread.join()
        url_matching_thread.join()
        custom_matching_thread.join()

        print("exiting")
        # PercolatorQuery(from_time, end_time).enter()
