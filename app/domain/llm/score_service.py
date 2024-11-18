import os
from app.domain.product.product_claim_repository import ProductClaimRepository


# get lower and get harder to match
QUALIFY_DISTANCE_RANGE = os.getenv('QUALIFY_DISTANCE_RANGE', '0.7')

class ScoreService:

    @classmethod
    async def get_or_add_top_infringing(cls, company_id, patent_id, limit=2):
        # NOTE needs a cron job for maintain the scores, due to product growing
        scores = await ProductClaimRepository.get_top_product_patent_scores(company_id, patent_id, limit)
        if len(scores) == 0:
            await ProductClaimRepository.add_product_patent_score(company_id=company_id, patent_id=patent_id)
            scores = await ProductClaimRepository.get_top_product_patent_scores(company_id, patent_id, limit)
        return scores