# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Integer

Base = declarative_base()

class Goal(Base):

    __tablename__ = 'goal'

    id =  Column(BigInteger, primary_key=True)
    name = Column(String(50))
    description =  Column( String)
    match_attribute =  Column( String(100) )
    match_pattern =  Column( String(100))
    match_pattern_type =   Column( String(50) )
    case_sensitive  =   Column( Integer)
    allow_multiple =   Column( Integer)
    revenue =   Column( Integer)
    conversion =   Column( Integer)
    app_id =  Column( String(50) )
    goal_attribute = Column(String(100) )
    goal_type =  Column( String(100) )
    goal_pattern =  Column( String(100))
    deleted =  Column( Integer)
