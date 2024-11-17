import json
from sqlalchemy import insert
from app.infrastructure.logger import logger
from app.infrastructure.database import async_session
from app.domain.product.models import CompanyModel, ProductModel

with open('assets/company_products.json') as json_file:
    data = json.load(json_file)

async def seeding_product():
    async with async_session() as session:
        try:
            logger.info("Seeding Company & Product...")
            for item in data["companies"]:
                # create company
                company = CompanyModel(name = item["name"])
                session.add(company)
                await session.flush()

                # bulk create product
                bulk = []
                for product in item['products']:
                    bulk.append(ProductModel(
                        company_id=company.id,
                        name = product['name'],
                        desc = product['description']
                    ).as_dict())
                stmt = insert(ProductModel).values(bulk)
                await session.execute(stmt)

            await session.commit()
            logger.info(f"{len(data['companies'])} Companies, {len(bulk)} Products seeded successfully.")

        except Exception as e:
            await session.rollback()
            logger.error("Error seeding products", exc_info=e)
        finally:
            await session.close()
