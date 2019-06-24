# coding=utf-8
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from external.query.url_matching_query import UrlMatchingGoalQuery
from external.database_init import DatabaseInit

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)


def query():
    hours_query = os.getenv('ELASTICSEARCH_HOURS_QUERY')
    from_time = (datetime.now() - timedelta(minutes = int(hours_query))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    end_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 
    print("######################################")
    print(" from_time %s - end_time: %s" %(from_time, end_time))
    result = DatabaseInit().get_data()

    UrlMatchingGoalQuery(result,from_time,end_time).enter_query()
    
# if __name__ == 'main':
query()
