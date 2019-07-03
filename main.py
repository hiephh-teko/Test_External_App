# coding=utf-8
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
from external.query.thread_query import ThreadQuery
# from external.query.url_matching_query import UrlMatchingGoalQuery
# from external.query.event_matching_query import EventMatchingGoalQuery
# from external.query.custom_matching_query import CustomMatchingQuery
# from external.database_init import DatabaseInit

from external.query.percolator_query import PercolatorQuery
_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)


def enter():
    print("run %s"%(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]))
    ThreadQuery().enter_thread()


enter()
