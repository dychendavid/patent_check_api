# database.py
import os, time
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from dotenv import load_dotenv
load_dotenv()  


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?client_encoding=utf8"
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now(), server_onupdate=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def wait_for_db(max_retries=30, retry_interval=2):
    print("Waiting for database ready")
    
    for attempt in range(max_retries):
        try:
            engine.connect()
            print("Database is ready!")
            return True            
        except Exception as e:
            print(f"Database not ready (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt + 1 < max_retries:
                time.sleep(retry_interval)    
    print("Failed to connect to database after maximum retries")
    exit(1)
 