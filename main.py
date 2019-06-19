# coding=utf-8
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from external.models.goal import Goal
from external.query.url_matching_query import UrlMatchingGoalQuery

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)

engine = create_engine(os.getenv('DATABASE_URI'))

connection = engine.connect()
metadata = db.MetaData()
goal_table = db.Table('goal', metadata, autoload=True, autoload_with=engine)
# site_tracking_description_table = db.Table('site_tracking_description', metadata, autoload=True, autoload_with=engine)

#create session
Session = sessionmaker(bind = engine)
session = Session()
    
def query():
    result = session.query(Goal).all()

    UrlMatchingGoalQuery(result).enter_query()
    

query()
