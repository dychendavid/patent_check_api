import json
import pydash
from sqlalchemy import insert
from app.infrastructure.utils import get_model_fields
from app.infrastructure.database import async_session
from app.infrastructure.logger import logger
from app.domain.patent.models import PatentModel, PatentClaimModel, PatentExtraModel

with open('assets/patents.json') as json_file:
    data = json.load(json_file)

async def seeding_patent():
    async with async_session() as session:
        try:
            logger.info("Seeding Patent...")
            for patent_data in data:
                # create patent
                patent_fields = get_model_fields(PatentModel, exclude=["id", "created_at", "updated_at"])
                filtered_data = pydash.pick(patent_data, patent_fields)
                patent = PatentModel(**filtered_data)
                session.add(patent)
                await session.flush()

                # bulk create claims
                claims_data = json.loads(patent_data["claims"])
                bulk = []
                for claim in claims_data:
                    bulk.append(PatentClaimModel(
                        patent_id=patent.id,
                        num = claim['num'],
                        desc = claim['text']
                    ).as_dict())
                stmt = insert(PatentClaimModel).values(bulk)
                await session.execute(stmt)

                # create patent_extra for long column
                patent_extra = PatentExtraModel(
                    patent_id=patent.id,
                    abstract = patent_data['abstract'],
                    description = patent_data['description'].strip()
                )
                session.add(patent_extra)
                await session.commit()
            logger.info(f"{len(data)} Patents seeded successfully.")
        except Exception as e:
            await session.rollback()
            logger.error("Error seeding Patent", exc_info=e)
        finally:
            await session.close()
