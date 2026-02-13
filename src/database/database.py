
from sqlalchemy import create_engine 
from config.setting import DATABASE_URL
from sqlalchemy.orm import declarative_base , sessionmaker


engine= create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind = engine)

Base = declarative_base()