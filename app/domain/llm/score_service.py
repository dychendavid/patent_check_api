import os
from sqlalchemy.sql import text
from app.infrastructure.database import SessionLocal
from app.domain.llm.models import ProductClaimDistance, ProductPatentScore


# get lower and get harder to match
QUALIFY_DISTANCE_RANGE = os.getenv('QUALIFY_DISTANCE_RANGE', '0.7')

class ScoreService:

    @classmethod
    def getOrAddTopInfringing(cls, company_id, patent_id, limit=2):
        # NOTE needs a cron job for maintain the scores, due to product growing
        scores = cls.getTopInfringingAggClaims(company_id, patent_id, limit)
        if len(scores) == 0:
            cls.calculateAndInsertScores()
            scores = cls.getTopInfringingAggClaims(company_id, patent_id, limit)
        return scores

    @classmethod
    def getTopInfringingAggClaims(cls, company_id, patent_id, limit=2):
        db = SessionLocal()

        return db.query(ProductPatentScore) \
            .filter(ProductPatentScore.company_id==company_id, ProductPatentScore.patent_id==patent_id) \
            .order_by(ProductPatentScore.score.desc()).limit(limit).all()


    @classmethod
    def calculateAndInsertScores(cls):
        db = SessionLocal()

        # formula: sum up by claims which afford threshold, this way considered claim's contribution and relevants
        query = text(f"""INSERT INTO {ProductPatentScore.__tablename__} (company_id, product_id, product_name, product_desc, patent_id, claim_ids, claim_descs, score)
            SELECT pcd.company_id, pcd.product_id, p.name AS product_name, p.desc AS product_desc, pcd.patent_id,
            ARRAY_AGG(claim_id) AS claim_ids,
            ARRAY_AGG(claim_desc) AS claim_descs,
            SUM(1 - cosine_distance) AS score
            FROM {ProductClaimDistance.__tablename__} AS pcd
            JOIN products AS p ON pcd.product_id=p.id
            WHERE cosine_distance < {QUALIFY_DISTANCE_RANGE}
            GROUP BY pcd.product_id, pcd.company_id, pcd.patent_id, p.desc, p.name
        """)
        db.execute(query)
        db.commit()