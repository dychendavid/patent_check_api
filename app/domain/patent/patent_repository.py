from typing import List, Optional
from sqlalchemy import func, select
from app.infrastructure.database import async_session
from app.infrastructure.base_repository import BaseRepository
from app.domain.patent.models import PatentModel


class PatentRepository(BaseRepository):
    @classmethod
    async def get_by_id(cls, item_id: int) -> Optional[PatentModel]:
        return super().get_by_model_id(PatentModel, item_id)

    @classmethod
    async def search_patent(cls, search_term, similarity_threshold=0.3):
        async with async_session() as session:
            stmt = select(PatentModel) \
                .filter(
                    (func.similarity(PatentModel.publication_number, search_term) > similarity_threshold)
                ).order_by(
                    func.similarity(PatentModel.publication_number, search_term).desc()
                )
        
            return await session.scalar(stmt)
