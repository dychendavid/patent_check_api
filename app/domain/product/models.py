from sqlalchemy import Column, Integer, String, UniqueConstraint, Index
from pgvector.sqlalchemy import Vector
from app.infrastructure.database import BaseModel


class CompanyModel(BaseModel):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    __table_args__ = (
        Index(
            'idx_company_name_gin_trgm',
            'name',
            postgresql_using='gin',
            postgresql_ops={'name': 'gin_trgm_ops'}
        ),
    )

class ProductModel(BaseModel):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    name = Column(String)
    desc = Column(String)

    __table_args__ = (UniqueConstraint('company_id', 'name', name='_company_name_uc'),)


class ProductVectorModel(BaseModel):
    __tablename__ = 'product_vectors'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    desc = Column(String)
    desc_vector = Column(Vector(1536))
