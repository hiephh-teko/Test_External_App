# coding=utf-8
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)

from external.query.thread_query import ThreadQuery

def enter():
    print("############ START JOB ############")
    ThreadQuery().enter_thread()

enter()
