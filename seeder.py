import asyncio
from app.infrastructure.logger import logger
from app.infrastructure.database import engine, Base
from seeds.patent import seeding_patent
from seeds.product import seeding_product
from seeds.embedding import seeding_claim_vector, seeding_product_vector

# discover table to inherite from Base
import app.domain.patent.models
import app.domain.product.models
import app.domain.llm.models
import app.domain.analysis.models


async def init():
    async with engine.begin() as conn:
        logger.info("Dropping all tables.")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Creating all tables.")
        await conn.run_sync(Base.metadata.create_all)

    # seeding
    await seeding_patent()
    await seeding_product()

    # embedding must after patent & product
    await seeding_claim_vector()
    await seeding_product_vector()


if __name__ == "__main__":
    asyncio.run(init())
