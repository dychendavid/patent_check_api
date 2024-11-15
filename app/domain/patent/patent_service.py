from sqlalchemy import func
from app.infrastructure.database import SessionLocal
from app.domain.patent.models import PatentModel


class PatentService:
    @classmethod
    def search_patent(cls, search_term, similarity_threshold=0.3):
        db = SessionLocal()
        row = db.query(
            PatentModel,
        ).filter(
            (func.similarity(PatentModel.publication_number, search_term) > similarity_threshold)
        ).order_by(func.similarity(PatentModel.publication_number, search_term).desc()).first()
        return row
