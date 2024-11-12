import json
from typing import List
from datetime import datetime
from sqlalchemy import select, func, text
from app.infrastructure.database import SessionLocal
from app.domain.patent.models import PatentModel
from app.domain.product.models import ProductModel, CompanyModel
from app.domain.llm.llm_service import LLMService
from app.domain.llm.models import ProductClaimDistance, ProductPatentScore
from app.domain.llm.score_service import ScoreService
from app.domain.analysis.models import AnalysisProductModel, AnalysisModel, UserAnalysisModel
from app.domain.analysis.scheme import APIAnalysisProductScheme, APIAnalysisScheme, LLMInfringementAnalysisScheme

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
        if (len(scores) == 0):
            raise Exception

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

    @classmethod
    def get_history_analysis(cls, user_id: int, status: int):
        db = SessionLocal()

        stmt = (
            select(
                AnalysisModel.id.label('analysis_id'),
                AnalysisModel.assessment.label('overall_risk_assessment'),
                PatentModel.publication_number.label('patent_id'),
                CompanyModel.name.label('company_name'),
                AnalysisModel.created_at.label('analysis_date'),
                func.json_agg(
                    func.json_build_object(
                        'product_name', ProductModel.name,
                        'infringement_likelihood', AnalysisProductModel.likelihood,
                        'specific_features', AnalysisProductModel.features,
                        'explanation', AnalysisProductModel.explanation,
                        'relevant_claims', AnalysisProductModel.claim_ids,
                )).label('top_infringing_products'),
            )
            .select_from(UserAnalysisModel)
            .join(AnalysisModel, UserAnalysisModel.analysis_id==AnalysisModel.id)
            .join(AnalysisProductModel, AnalysisModel.id==AnalysisProductModel.analysis_id)

            .join(ProductModel, AnalysisProductModel.product_id==ProductModel.id)
            .join(CompanyModel, AnalysisModel.company_id==CompanyModel.id) \
            .join(PatentModel, PatentModel.id==AnalysisModel.patent_id) \

            .filter(UserAnalysisModel.user_id==user_id, UserAnalysisModel.status==status) \
            .group_by(
                    AnalysisModel.id,
                    CompanyModel.name,
                    PatentModel.publication_number,
                    AnalysisModel.assessment, 
                    AnalysisModel.created_at,
                    )
        )

        return db.execute(stmt).mappings().all()    
