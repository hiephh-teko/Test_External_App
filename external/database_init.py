import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy as db
from external.models.goal import Goal
from sqlalchemy.orm import sessionmaker

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(_DOT_ENV_PATH)


class DatabaseInit(object):
    def __init__(self):
        engine = create_engine(os.getenv('DATABASE_URI'))
        connection = engine.connect()
        metadata = db.MetaData()
        goal_table = db.Table('goal', metadata, autoload=True, autoload_with=engine)
        
        #create session
        Session = sessionmaker(bind = engine)
        self.session = Session()

    def get_data(self):
        result = self.session.query(Goal).all()
        return result