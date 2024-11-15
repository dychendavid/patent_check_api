from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.infrastructure.database import get_db
from app.domain.patent.models import PatentModel
from app.domain.patent.patent_service import PatentService
from app.domain.product.models import CompanyModel
from app.domain.product.product_service import ProductService
from app.domain.analysis.models import UserAnalysisModel
from app.domain.analysis.scheme import APISaveAnalysisScheme
from app.domain.analysis.analysis_service import AnalysisService

router = APIRouter()


@router.post("/api/v1/analysis/check")
def check_infringement(publication_number: str, company_name: str, db:Session = Depends(get_db)):
    company:CompanyModel = ProductService.search_company(company_name)
    if company is None:
        raise HTTPException(status_code=404, detail={'message': "Company not found"})

    patent:PatentModel = PatentService.search_patent(publication_number)
    if patent is None:
        raise HTTPException(status_code=404, detail={'message': "Patent not found"})

    try:
        result = AnalysisService.check_infringement(patent.id, company.id)
    except Exception as e :
        raise HTTPException(status_code=404, detail={'message': "Infringement not found"}) from e 
        
    return AnalysisService.output_formatter(publication_number=patent.publication_number, \
                                                    company_name=company.name, \
                                                    llm_res=result["res_json"], \
                                                    analysis=result["analysis"])
    

@router.get("/api/v1/analysis/saved")
def get_saved_analyses(user_id:int):
    return AnalysisService.get_history_analysis(user_id, 1)
    

@router.post("/api/v1/analysis")
def update_analysis_status(data:APISaveAnalysisScheme, db:Session = Depends(get_db)):
    row = data.model_dump()
    update_cols = {
        col.name: row[col.name]
        for col in UserAnalysisModel.__table__.columns
        if col.name not in ['id', 'created_at', 'updated_at']
    }

    # update on Unique(user_id * analysis_id) 
    stmt = pg_insert(UserAnalysisModel).values(row)
    stmt = stmt.on_conflict_do_update(
        constraint='_user_analysis_uc',
        set_=update_cols
    )

    db.execute(stmt)
    db.commit()
    return {"message":"ok"}


