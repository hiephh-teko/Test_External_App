import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy as db
from external.models.goal import Goal
from sqlalchemy.orm import sessionmaker


class DatabaseInit(object):
    def __init__(self):
        engine = create_engine(os.getenv('DATABASE_URI'))
        self.connection = engine.connect()
        metadata = db.MetaData()
        self.goal_table = db.Table('goal_definition', metadata, autoload=True, autoload_with=engine)
        
        #create session
        Session = sessionmaker(bind = engine)
        self.session = Session()

    def get_data_event_matching(self):
        result = self.session.query(Goal).filter(Goal.goal_type == 'event', Goal.activeness == 1)
        return result

    def get_data_url_matching(self):
        result = self.session.query(Goal).filter(Goal.goal_type == 'url', Goal.activeness == 1)
        return result

    def get_data_custom_matching(self):
        result = self.session.query(Goal).filter(Goal.goal_type == 'custom_matching')
        return result