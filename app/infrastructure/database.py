import os
from sqlalchemy import inspect, Column, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)
Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now(), server_onupdate=func.now())

    def as_dict(self, exclude=["id", "created_at", "updated_at"]):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if c.key not in exclude
        }