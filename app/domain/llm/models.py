from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, DateTime, UniqueConstraint
from sqlalchemy.types import ARRAY
from pgvector.sqlalchemy import Vector

from app.infrastructure.database import BaseModel


class ProductClaimDistance(BaseModel):
    __tablename__ = 'product_claim_distances'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer)
    product_id = Column(Integer)
    product_desc = Column(String)
    patent_id = Column(Integer)
    claim_id = Column(Integer)    
    claim_desc = Column(String)
    cosine_distance = Column(Float)


class ProductPatentScore(BaseModel):
    __tablename__ = 'product_patent_scores'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer)
    product_id = Column(Integer)
    patent_id = Column(Integer)
    product_name = Column(String)
    product_desc = Column(String)
    claim_ids = Column(ARRAY(Integer))
    claim_descs = Column(ARRAY(String))
    score = Column(Float)