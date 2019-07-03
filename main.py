# coding=utf-8
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
from external.query.url_matching_query import UrlMatchingGoalQuery
from external.query.event_matching_query import EventMatchingGoalQuery
from external.query.custom_matching_query import CustomMatchingQuery
from external.database_init import DatabaseInit

from external.query.percolator_query import PercolatorQuery
_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)


def query():
    print("run")
    hours_query = os.getenv('ELASTICSEARCH_HOURS_QUERY')
    # from_time = (datetime.now() - timedelta(minutes = int(hours_query))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    # end_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 

    from_time = "2019-06-25T13:18:22.000"
    end_time = "2019-06-25T23:59:59.000"

    # event_matching_data = DatabaseInit().get_data_event_matching()  
    # EventMatchingGoalQuery(event_matching_data,from_time,end_time).enter_query()

    # url_matching_data = DatabaseInit().get_data_url_matching()
    # UrlMatchingGoalQuery(url_matching_data,from_time,end_time).enter_query()

    # custom_matching_data = DatabaseInit().get_data_custom_matching()
    # CustomMatchingQuery(custom_matching_data,from_time, end_time).enter_query()

    PercolatorQuery(from_time, end_time).enter()


query()
