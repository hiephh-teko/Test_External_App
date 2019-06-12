# coding=utf-8
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)

engine = create_engine(os.getenv('DATABASE_URI'))

sql = text('SELECT 1')

result = engine.execute(sql)

data = [row[0] for row in result]

print(data)
