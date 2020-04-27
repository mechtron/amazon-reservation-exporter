# coding=utf-8

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_HOSTNAME = os.environ.get("DATABASE_HOSTNAME")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_NAME = os.environ.get("DATABASE_NAME")


engine = create_engine(
    "postgresql://{username}:{password}@{host}/{db_name}".format(
        username=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOSTNAME,
        db_name=DATABASE_NAME,
    )
)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def generate_database_schema():
    print("Generating database schema..")
    Base.metadata.create_all(engine)
