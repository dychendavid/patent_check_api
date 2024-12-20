from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import ARRAY
from app.infrastructure.database import BaseModel


class ProductClaimDistanceModel(BaseModel):
    __tablename__ = 'product_claim_distances'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer)
    product_id = Column(Integer, index=True)
    product_desc = Column(String)
    patent_id = Column(Integer)
    claim_id = Column(Integer, index=True)    
    claim_desc = Column(String)
    cosine_distance = Column(Float)


class ProductPatentScoreModel(BaseModel):
    __tablename__ = 'product_patent_scores'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer)
    product_id = Column(Integer, index=True)
    patent_id = Column(Integer, index=True)
    product_name = Column(String)
    product_desc = Column(String)
    claim_ids = Column(ARRAY(Integer))
    claim_descs = Column(ARRAY(String))
    score = Column(Float)