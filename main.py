# coding=utf-8
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from goal import Goal
from elasticsearch_connect import ElasticsearchConnect

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
    # query = db.select([goal_table])
    # ResultPoroxy = connection.execute(query)
    # Res = ResultPoroxy.fetchall()
    # print(Res)
    
    columns = [Goal.match_attribute, Goal.pattern, Goal.pattern_type]
    result = session.query(Goal).with_entities(*columns).all()
    
    ElasticsearchConnect(result).open_connect()
    # for c, i in session.query(goal_table, site_tracking_description_table).filter(goal_table.client_id == site_tracking_description_table.client_id).all:
    

# if __name__ == '__main__':
query()

# print(goals.columns.keys())
# print(repr(metadata.tables['goals']))


# sql = text('SELECT 1')

# result = engine.execute(sql)

# data = [row[0] for row in result]

# print(data)