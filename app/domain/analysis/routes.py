from fastapi import APIRouter, HTTPException
from app.infrastructure.logger import logger

from app.domain.patent.models import PatentModel
from app.domain.patent.patent_repository import PatentRepository
from app.domain.product.models import CompanyModel
from app.domain.product.company_repository import CompanyRepository 
from app.domain.analysis.scheme import APISaveAnalysisScheme
from app.domain.analysis.analysis_service import AnalysisService
from app.domain.analysis.analysis_repository import AnalysisRepository

router = APIRouter()


@router.post("/api/v1/analysis/check")
async def check_infringement(publication_number: str, company_name: str):
    company:CompanyModel = await CompanyRepository.search_company(company_name)
    if company is None:
        raise HTTPException(status_code=404, detail={'message': "Company not found"})

    patent:PatentModel = await PatentRepository.search_patent(publication_number)
    if patent is None:
        raise HTTPException(status_code=404, detail={'message': "Patent not found"})

    try:
        result = await AnalysisService.check_infringement(patent.id, company.id)
    except Exception as e :
        logger.error('check_infringement_error', exc_info=e)
        raise HTTPException(status_code=404, detail={'message': "Infringement not found"}) from e 
        
    return AnalysisService.output_formatter(publication_number=patent.publication_number, \
                                                    company_name=company.name, \
                                                    llm_res=result["res_json"], \
                                                    analysis=result["analysis"])
    

@router.get("/api/v1/analysis/saved")
async def get_saved_analyses(user_id:int):
    return await AnalysisRepository.get_history_analyses(user_id, 1)
    

@router.post("/api/v1/analysis")
async def update_analysis_status(data:APISaveAnalysisScheme):
    await AnalysisRepository.update_row_on_dupliate(data.model_dump())
    return {"message":"ok"}


