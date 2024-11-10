from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, DateTime, UniqueConstraint
from pgvector.sqlalchemy import Vector

from app.infrastructure.database import BaseModel


class PatentModel(BaseModel):
    __tablename__ = 'patents'
    id = Column(Integer, primary_key=True, index=True)
    publication_number = Column(String, unique=True)
    title = Column(String)
    ai_summary = Column(String)
    raw_source_url = Column(String)
    assignee = Column(String)
    inventors = Column(JSON)
    priority_date = Column(String)
    application_date = Column(String)
    grant_date = Column(String)
    jurisdictions = Column(String)
    classifications = Column(JSON)
    application_events = Column(String)
    citations = Column(JSON)
    image_urls = Column(JSON)
    landscapes = Column(String)
    publish_date = Column(String)
    citations_non_patent = Column(String)
    provenance = Column(String)
    attachment_urls = Column(String)

class PatentClaimModel(BaseModel):
    __tablename__ = 'patent_claims'
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer)
    num = Column(String)
    desc = Column(String)
    __table_args__ = (UniqueConstraint('patent_id', 'num', name='_patent_num_uc'),)


class PatentExtraModel(BaseModel):
    __tablename__ = 'patent_extras'
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, unique=True)
    abstract = Column(Text)
    description = Column(Text)

class PatentClaimVectorModel(BaseModel):
    __tablename__ = 'patent_claim_vectors'
    id = Column(Integer, primary_key=True, index=True)    
    patent_id = Column(Integer)
    claim_id = Column(Integer)
    desc = Column(String)
    desc_vector = Column(Vector(1536))

