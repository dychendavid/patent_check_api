import os
from sqlalchemy import text, select
from app.infrastructure.database import async_session
from app.infrastructure.base_repository import BaseRepository
from app.domain.llm.models import ProductClaimDistanceModel
from app.domain.llm.models import ProductPatentScoreModel

QUALIFY_DISTANCE_RANGE = os.getenv('QUALIFY_DISTANCE_RANGE', '0.7')


class ProductClaimRepository(BaseRepository):
    @classmethod
    async def check_by_company_patent_id(
        cls, company_id: int, patent_id: int
    ):
        async with async_session() as session:
            stmt = select(ProductClaimDistanceModel).where(
                    ProductClaimDistanceModel.company_id == company_id,
                    ProductClaimDistanceModel.patent_id == patent_id,
                )

            result = await session.execute(stmt)
            return result.first()

                        
    @classmethod
    async def add_vector_distances(cls, company_id:int, patent_id:int):
        """
        Calculate and store cosine distances between product descriptions and patent claims vectors.
        
        This method performs a cross-join between product_vectors and patent_claim_vectors tables
        to compute cosine distances between product descriptions and patent claims for a specific
        company and patent. The results are stored in the product_claim_distance table.
        """

        async with async_session() as session:
            stmt = text(f"""
                INSERT INTO {ProductClaimDistanceModel.__tablename__} (company_id, product_id, product_desc, patent_id, claim_id, claim_desc, cosine_distance)
                SELECT
                pv.company_id,
                pv.product_id,
                pv.desc AS product_desc,
                pcv.patent_id,
                pcv.claim_id,
                pcv.desc AS claim_desc,
                (pcv.desc_vector <=> pv.desc_vector) AS cosine_distance
                FROM patent_claim_vectors AS pcv, product_vectors AS pv
                WHERE pv.company_id={company_id} AND pcv.patent_id={patent_id}
            """)
            await session.execute(stmt)
            await session.commit()



    @classmethod
    async def add_product_patent_score(cls, company_id:int, patent_id:int):

        async with async_session() as session:
            stmt = text(f"""INSERT INTO {ProductPatentScoreModel.__tablename__} (company_id, product_id, product_name, product_desc, patent_id, claim_ids, claim_descs, score)
                SELECT pcd.company_id, pcd.product_id, p.name AS product_name, p.desc AS product_desc, pcd.patent_id,
                ARRAY_AGG(claim_id) AS claim_ids,
                ARRAY_AGG(claim_desc) AS claim_descs,
                SUM(1 - cosine_distance) AS score
                FROM {ProductClaimDistanceModel.__tablename__} AS pcd
                JOIN products AS p ON pcd.product_id=p.id
                WHERE cosine_distance < {QUALIFY_DISTANCE_RANGE} AND pcd.company_id={company_id} AND pcd.patent_id={patent_id}
                GROUP BY pcd.product_id, pcd.company_id, pcd.patent_id, p.desc, p.name
            """)
            await session.execute(stmt)
            await session.commit()


    @classmethod
    async def get_top_product_patent_scores(cls, company_id, patent_id, limit=2):
        async with async_session() as session:

            stmt = select(ProductPatentScoreModel) \
                .where(ProductPatentScoreModel.company_id==company_id, ProductPatentScoreModel.patent_id==patent_id) \
                .order_by(ProductPatentScoreModel.score.desc()).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
            
