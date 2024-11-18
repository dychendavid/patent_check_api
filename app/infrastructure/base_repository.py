from sqlalchemy import select, insert
from app.infrastructure.database import async_session

class BaseRepository:
    @classmethod
    async def get_by_model_id(cls, model, item_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(model).filter(model.id == item_id)
            )
            return result.scalar_one_or_none()