from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class APISaveAnalysisScheme(BaseModel):
    user_id: int
    analysis_id: int
    status: int


# for api to client output format
class APIAnalysisProductScheme(BaseModel):
    product_name: str
    infringement_likelihood: str
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class APIAnalysisScheme(BaseModel):
    analysis_id: str
    patent_id: str
    company_name: str
    analysis_date: str
    top_infringing_products: List[APIAnalysisProductScheme]
    overall_risk_assessment: str

# for llm to backend output format
class LLMInfringementProductScheme(BaseModel):
    product_id: int
    product_name: str
    likelihood: str = Field(descriptio="infringement likelihood, ex: Low, Medium, High")
    claim_ids: List[int] = Field(descriptin="relevant claims")
    explanation: str = Field(description="your inference, consider what scenarios this product faced, and analyze whats the implementation, and how the approaches infringing patent claim")
    features: List[str] = Field(description="specific features")


class LLMInfringementAnalysisScheme(BaseModel):
    risk_level: str = Field(description="overall risk level, ex: Low, Medium, High")
    assessment: str = Field(description="assessment of overall risk, highlight the most risk product and implementation, and relevant patent infringement")
    products: List[LLMInfringementProductScheme] = Field(description="top infringing products")
    


