import json
from typing import List
from datetime import datetime
from sqlalchemy import insert
from app.infrastructure.database import async_session
from app.domain.llm.llm_service import LLMService
from app.domain.llm.models import ProductPatentScoreModel
from app.domain.llm.score_service import ScoreService
from app.domain.analysis.models import AnalysisProductModel, AnalysisModel
from app.domain.analysis.scheme import APIAnalysisProductScheme, APIAnalysisScheme, LLMInfringementAnalysisScheme
from app.domain.product.product_claim_repository import ProductClaimRepository

class AnalysisService:    
    @classmethod
    def output_formatter(cls, publication_number:str, company_name: str, llm_res:LLMInfringementAnalysisScheme, analysis:dict) -> str:
        analysis_date:datetime = analysis["created_at"]

        products = [APIAnalysisProductScheme(
            product_name=product["product_name"],
            infringement_likelihood=product["likelihood"],
            relevant_claims = [str(claim_id) for claim_id in product['claim_ids']],
            explanation= product['explanation'],
            specific_features=product['features'])
            for product in llm_res['products']]

        return APIAnalysisScheme(
            analysis_id=str(analysis["id"]),
            patent_id=publication_number,
            company_name=company_name,
            analysis_date=analysis_date.strftime("%Y-%m-%d"),
            overall_risk_assessment=analysis["assessment"],
            top_infringing_products=products)
    

    @classmethod
    async def check_infringement(cls, patent_id: int, company_id: int):
        async with async_session() as session:
            # runtime calculate distance if first time
            # NOTE later could optimized as cron version, don't calculate on runtime for better experience
            if await ProductClaimRepository.check_by_company_patent_id(company_id=company_id, patent_id=patent_id) is None:
                # bulk calculate cosine distance between claim desc and product desc
                # 1 company have N products
                # 1 product compared to M claims
                # this will add N * M distance (rows)
                await ProductClaimRepository.add_vector_distances(company_id=company_id, patent_id=patent_id)

            # get top infriniging with claim desc and product desc
            scores:List[ProductPatentScoreModel] = await ScoreService.get_or_add_top_infringing(company_id, patent_id)
            if (len(scores) == 0):
                raise Exception('No ProductPatentScore')

            # ask llm & save analysis
            res_text = LLMService.check_infringing_by_chat_open_ai(scores)
            res_json = json.loads(res_text)
            analysis = AnalysisModel(
                risk_level=res_json["risk_level"],
                assessment=res_json["assessment"],
                company_id=company_id,
                patent_id=patent_id
            )
            session.add(analysis)
            await session.flush()

            # bulk insert products of analysis
            products = [AnalysisProductModel(
                analysis_id=analysis.id,
                product_id=product["product_id"],
                claim_ids=product["claim_ids"],
                likelihood=product["likelihood"],
                explanation=product["explanation"],
                features=product["features"]                    
            ).as_dict() for product in res_json['products']]
            stmt = insert(AnalysisProductModel).values(products)
            await session.execute(stmt)

            await session.commit()
            return {
                "res_json": res_json,
                "analysis": analysis.as_dict(exclude=[]),
            }
