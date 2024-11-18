from typing import List, Optional
from sqlalchemy import select, func
from app.infrastructure.database import async_session
from app.infrastructure.base_repository import BaseRepository
from app.domain.product.models import CompanyModel


class CompanyRepository(BaseRepository):
    @classmethod
    async def get_by_id(cls, item_id: int) -> Optional[CompanyModel]:
        return await super().get_by_model_id(CompanyModel, item_id)

    @classmethod
    async def search_company(cls, search_term, similarity_threshold=0.3):
        async with async_session() as session:
            stmt = select(CompanyModel) \
                .filter(
                    (func.similarity(CompanyModel.name, search_term) > similarity_threshold)
                ).order_by(
                    func.similarity(CompanyModel.name, search_term).desc()
                )
        
            return await session.scalar(stmt)