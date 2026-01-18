from sqlalchemy.orm.session import Session


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL connection string
# Update with your MySQL credentials
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/microservice_demo"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Base.metadata.create_all(bind=engine)