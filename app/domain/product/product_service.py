from sqlalchemy import func
from app.infrastructure.database import SessionLocal
from app.domain.product.models import CompanyModel


class ProductService:
    @classmethod
    def search_company(cls, search_term, similarity_threshold=0.3):
        db = SessionLocal()
        row = db.query(
            CompanyModel
        ).filter(
            (func.similarity(CompanyModel.name, search_term) > similarity_threshold)
        ).order_by(func.similarity(CompanyModel.name, search_term).desc()).first()
        return row
