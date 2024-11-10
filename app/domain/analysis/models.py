import enum
from sqlalchemy import Column, Integer, String, Enum, Text, UniqueConstraint
from sqlalchemy.types import ARRAY

from app.infrastructure.database import BaseModel



class LevelEnum(str, enum.Enum):
    Low = 1
    Medium = 2
    High = 3

class AnalysisModel(BaseModel):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer)
    company_id = Column(Integer)
    assessment = Column(Text)
    risk_level = Column(Enum(LevelEnum))


class AnalysisProductModel(BaseModel):
    __tablename__ = "analysis_products"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer)
    product_id = Column(Integer)
    claim_ids = Column(ARRAY(Integer))
    likelihood = Column(Enum(LevelEnum))
    explanation = Column(Text)
    features = Column(ARRAY(String))


class UserAnalysisModel(BaseModel):
    __tablename__ = "user_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    analysis_id = Column(Integer)
    status = Column(Integer)

    __table_args__ = (UniqueConstraint('user_id', 'analysis_id', name='_user_analysis_uc'),)
