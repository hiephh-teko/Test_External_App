# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Boolean

Base = declarative_base()

class Goal(Base):

    __tablename__ = 'goal'

    id =  Column(BigInteger, primary_key=True)
    description =  Column( String)
    match_attribute =  Column( String(100) )
    pattern =  Column( String(100))
    pattern_type =   Column( String(50) )
    case_sensitive  =   Column( Boolean)
    allow_multiple =   Column( Boolean)
    revenue =   Column( Boolean)
    conversion =   Column( Boolean)
    client_id =  Column( BigInteger )
    goal_type =  Column( String(100) )
    goal_pattern =  Column( String(100))
    deleted =  Column( Boolean)
