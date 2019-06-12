# coding=utf-8
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy as db


_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)

engine = create_engine(os.getenv('DATABASE_URI'))

connection = engine.connect()
metadata = db.MetaData()
goals = db.Table('goals', metadata, autoload=True, autoload_with=engine)

query = db.select([goals])
ResultPoroxy = connection.execute(query)
Res = ResultPoroxy.fetchall()
print(Res)

# print(goals.columns.keys())
# print(repr(metadata.tables['goals']))


# sql = text('SELECT 1')

# result = engine.execute(sql)

# data = [row[0] for row in result]

# print(data)
