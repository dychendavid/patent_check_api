from fastapi import Depends, APIRouter, HTTPException
# from app.infrastructure.message_broker.rabbitmq import consume
from sqlalchemy import select, func, text, update
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.infrastructure.database import get_db
from app.domain.analysis.models import AnalysisModel, AnalysisProductModel
from app.domain.patent.models import PatentModel, PatentClaimModel
from app.domain.analysis.models import UserAnalysisModel
from app.domain.analysis.scheme import APISaveAnalysisScheme, APIAnalysisScheme, APIAnalysisProductScheme
from app.domain.analysis.analysis_service import AnalysisService
from app.domain.product.models import CompanyModel, ProductModel
from typing import get_type_hints


router = APIRouter()


@router.post("/api/v1/analysis/check")
def check_infringement(publication_number: str, company_name: str, db:Session = Depends(get_db)):
    # TODO make it afford to fuzzy match with CompanyModel.name_vector
    company:CompanyModel = db.query(CompanyModel).filter(CompanyModel.name==company_name).first()
    if company is None:
        raise HTTPException(status_code=404, detail={'message': "No Result Found"})

    patent:PatentModel = db.query(PatentModel).filter(PatentModel.publication_number==publication_number).first()
    if patent is None:
        raise HTTPException(status_code=404, detail={'message': "No Result Found"})


    result = AnalysisService.check_infringement(patent.id, company.id)
    return AnalysisService.output_formatter(publication_number=publication_number, \
                                                    company_name=company_name, \
                                                    llm_res=result["res_json"], \
                                                    analysis=result["analysis"])
    

@router.get("/api/v1/analysis/saved")
def getSavedAnalysis(user_id:int, db:Session = Depends(get_db)):
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

        .filter(UserAnalysisModel.user_id==user_id, UserAnalysisModel.status==1) \
        .group_by(
                AnalysisModel.id,
                CompanyModel.name,
                PatentModel.publication_number,
                AnalysisModel.assessment, 
                AnalysisModel.created_at,
                  )
    )

    print(stmt)
    rows = db.execute(stmt).mappings().all()    
    print(len(rows))
    return rows

    

@router.post("/api/v1/analysis")
def updateAnalysisStatus(data:APISaveAnalysisScheme, db:Session = Depends(get_db)):
    row = data.model_dump()

    update_cols = {
        col.name: row[col.name]
        for col in UserAnalysisModel.__table__.columns
        if col.name not in ['id', 'created_at', 'updated_at']
    }
    stmt = pg_insert(UserAnalysisModel).values(row)
    stmt = stmt.on_conflict_do_update(
        constraint='_user_analysis_uc',
        set_=update_cols
    )

    print(stmt)
    db.execute(stmt)
    db.commit()
    return {"message":"ok"}


