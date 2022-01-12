#! /usr/bin/python3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

SQLALCHEMY_DATABASE_URL = "mysql://"+config.mysql['user']+":"+config.mysql['passwd']+"@"+config.mysql['host']+"/"+config.mysql['db']+"?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,encoding='utf8', convert_unicode=True, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


