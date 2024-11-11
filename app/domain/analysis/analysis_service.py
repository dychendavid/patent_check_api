import json
from typing import List
from fastapi import Depends
from datetime import datetime
from sqlalchemy import Select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.infrastructure.database import engine, SessionLocal, get_db
from app.domain.patent.models import PatentModel, PatentClaimModel
from app.domain.product.models import ProductModel, CompanyModel
from app.domain.llm.llm_service import LLMService
from app.domain.llm.models import ProductClaimDistance, ProductPatentScore
from app.domain.llm.score_service import ScoreService
from app.domain.analysis.models import AnalysisProductModel, AnalysisModel, LevelEnum
from app.domain.analysis.scheme import APIAnalysisProductScheme, APIAnalysisScheme, LLMInfringementAnalysisScheme, LLMInfringementProductScheme

class AnalysisService:
    def output_formatter(publication_number:str, company_name: str, llm_res:LLMInfringementAnalysisScheme, analysis:dict) -> str:
        analysis_date:datetime = analysis["created_at"]

        products = [APIAnalysisProductScheme(
            product_name=product["product_name"],
            infringement_likelihood=product["likelihood"],
            relevant_claims = [str(claim_id) for claim_id in product['claim_ids']],
            explanation= product['explanation'],
            specific_features=product['features'])
            for product in llm_res['products']]
        print(analysis)
        return APIAnalysisScheme(
            analysis_id=str(analysis["id"]),
            patent_id=publication_number,
            company_name=company_name,
            analysis_date=analysis_date.strftime("%Y-%m-%d"),
            overall_risk_assessment=analysis["assessment"],
            top_infringing_products=products)
    
    def output_formatter2(analysis:dict) -> str:
        analysis_date:datetime = analysis["created_at"]
        print('analysis', type(analysis))
        print('analysis products', type(analysis["products"]))
        for p in analysis['products']:
            print(p)

        products = [APIAnalysisProductScheme(
            product_name=product["product_name"],
            infringement_likelihood=product["likelihood"],
            relevant_claims = [str(claim_id) for claim_id in product['claim_ids']],
            explanation= product['explanation'],
            specific_features=product['features'])
            for product in analysis['products']]
                
        return APIAnalysisScheme(
            analysis_id=str(analysis["id"]),
            patent_id=analysis["publication_number"],
            company_name=analysis["company_name"],
            analysis_date=analysis_date.strftime("%Y-%m-%d"),
            overall_risk_assessment=analysis["assessment"],
            top_infringing_products=products)


    @classmethod
    def check_infringement(cls, patent_id: int, company_id: int):
        db = SessionLocal()

        # runtime calculate distance if first time
        # NOTE later could optimized as cron version, don't calculate on runtime for better experience
        if db.query(ProductClaimDistance).filter(CompanyModel.id==company_id, PatentModel.id==patent_id).first() is None:
            # bulk calculate cosine distance between claim desc and product desc
            # 1 company have N products
            # 1 product compared to M claims
            # this will add N * M distance (rows)
            statement = text(f"""
                INSERT INTO {ProductClaimDistance.__tablename__} (company_id, product_id, product_desc, patent_id, claim_id, claim_desc, cosine_distance)
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
            db.execute(statement)
            db.commit()

        # get top infriniging with claim desc and product desc
        scores:List[ProductPatentScore] = ScoreService.getOrAddTopInfringing(company_id, patent_id)

        # ask llm
        res_text = LLMService.checkInfringingByChatOpenAI(scores)
        res_json = json.loads(res_text)

        analysis = AnalysisModel(
            risk_level=res_json["risk_level"],
            assessment=res_json["assessment"],
            company_id=company_id,
            patent_id=patent_id
        )
        db.add(analysis)
        db.flush()

        products = [AnalysisProductModel(
            analysis_id=analysis.id,
            product_id=product["product_id"],
            claim_ids=product["claim_ids"],
            likelihood=product["likelihood"],
            explanation=product["explanation"],
            features=product["features"]                    
        ) for product in res_json['products']]            
        db.bulk_save_objects(products)

        db.commit()
        return {
            "res_json": res_json,
            "analysis": analysis.as_dict(),
        }

