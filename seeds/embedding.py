from sqlalchemy import insert, select
from app.infrastructure.logger import logger
from app.infrastructure.ai import AI
from app.infrastructure.database import async_session
from app.domain.product.models import ProductModel, ProductVectorModel
from app.domain.patent.models import PatentClaimVectorModel, PatentClaimModel

async def seeding_product_vector():
    async with async_session() as session:
        try:
            logger.info("Seeding ProductVector...")
            stmt = select(ProductModel)            
            result = await session.scalars(stmt)
            rows = result.all()

            # get embedding
            embeds = [claim.desc for claim in rows]
            embeddings = await AI.get_embeddings(embeds)

            # handle bulk insert
            bulk = []
            product:ProductModel
            for idx, product in enumerate(rows):
                bulk.append(ProductVectorModel(
                    company_id = product.company_id,
                    product_id = product.id,
                    desc = product.desc,
                    desc_vector = embeddings[idx],
                ).as_dict())
            stmt = insert(ProductVectorModel).values(bulk)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"{len(rows)} ProductVector seeded successfully.")
        except Exception as e:
            await session.rollback()
            logger.error("Error on seeds ProductVector", exc_info=e)
        finally:
            await session.close()

async def seeding_claim_vector():
    async with async_session() as session:
        try:
            logger.info("Seeding PatentClaimVector...")
            stmt = select(PatentClaimModel)
            result = await session.scalars(stmt)
            rows = result.all()
            
            # get embedding
            embeds = [claim.desc for claim in rows]
            embeddings = await AI.get_embeddings(embeds)

            # handle bulk insert
            bulk = []
            for idx, claim in enumerate(rows):
                bulk.append(PatentClaimVectorModel(
                    patent_id = claim.patent_id,
                    claim_id = claim.id,
                    desc = claim.desc,
                    desc_vector = embeddings[idx]

                ).as_dict())
            stmt = insert(PatentClaimVectorModel).values(bulk)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"{len(rows)} PatentClaimVector seeded successfully.")

        except Exception as e:
            await session.rollback()
            logger.error("Error seeding PatentClaimVector", exc_info=e)
        finally:
            await session.close()
