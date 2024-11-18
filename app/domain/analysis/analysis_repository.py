from typing import List, Optional
from sqlalchemy import select, func
from app.infrastructure.database import async_session
from app.infrastructure.base_repository import BaseRepository
from app.domain.product.models import CompanyModel, ProductModel
from app.domain.patent.models import PatentModel
from app.domain.analysis.models import UserAnalysisModel, AnalysisModel, AnalysisProductModel
from sqlalchemy.dialects.postgresql import insert as pg_insert


class AnalysisRepository(BaseRepository):
    @classmethod
    async def update_row_on_dupliate(cls, row:dict):
        async with async_session() as session:
            update_cols = {
                col.name: row[col.name]
                for col in UserAnalysisModel.__table__.columns
                if col.name not in ['id', 'created_at', 'updated_at']
            }

            # update on Unique(user_id, analysis_id) 
            stmt = pg_insert(UserAnalysisModel).values(row)
            stmt = stmt.on_conflict_do_update(
                constraint='_user_analysis_uc',
                set_=update_cols
            )

            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_history_analyses(cls, user_id: int, status: int):
        async with async_session() as session:
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
                .join(CompanyModel, AnalysisModel.company_id==CompanyModel.id)
                .join(PatentModel, PatentModel.id==AnalysisModel.patent_id)
                .filter(UserAnalysisModel.user_id==user_id, UserAnalysisModel.status==status)
                .group_by(
                    AnalysisModel.id,
                    CompanyModel.name,
                    PatentModel.publication_number,
                    AnalysisModel.assessment, 
                    AnalysisModel.created_at,
                )
            )
            result = await session.execute(stmt)
            return result.mappings().all()
