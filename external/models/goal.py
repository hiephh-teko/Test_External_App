# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Integer

Base = declarative_base()

class Goal(Base):

    __tablename__ = 'goal_definition'

    goal_id =  Column(BigInteger, primary_key=True)
    app_id = Column(String)
    goal_name =  Column( String)
    description =  Column( String )
    goal_type =  Column( String )
    goal_pattern = Column( String )
    pattern_type = Column( String )
    threshold =   Column( Integer)
    case_sensitive  =   Column( Integer)
    allow_multiple =   Column( Integer)
    deleted =  Column( Integer)
    activeness =   Column( Integer)

    
