from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = "postgresql://postgres:oiy3sisiz89zk@localhost:5432/e_commerce"

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit= False ,autoflush=False, bind = engine)

Base = declarative_base