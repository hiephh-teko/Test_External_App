# coding=utf-8
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
from external.query.url_matching_query import UrlMatchingGoalQuery
from external.query.event_matching_query import EventMatchingGoalQuery
from external.query.custom_matching_query import CustomMatchingQuery
from external.query.visiting_duration_matching_query import VisitingDurationMatching
from external.database_init import DatabaseInit

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)


def query():
    print("run")
    hours_query = os.getenv('ELASTICSEARCH_HOURS_QUERY')
    from_time = (datetime.now() - timedelta(minutes = int(hours_query))).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    end_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] 

    # event_matching_data = DatabaseInit().get_data_event_matching()  
    # EventMatchingGoalQuery(event_matching_data,from_time,end_time).enter_query()

    # url_matching_data = DatabaseInit().get_data_url_matching()
    # UrlMatchingGoalQuery(url_matching_data,from_time,end_time).enter_query()

    # custom_matching_data = DatabaseInit().get_data_custom_matching()
    # CustomMatchingQuery(custom_matching_data,from_time, end_time).enter_query()

    visiting_duration_matching_data = DatabaseInit().get_data_visiting_duration_matching()
    VisitingDurationMatching(visiting_duration_matching_data,from_time,end_time).enter_query()

query()
