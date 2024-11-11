from pydantic import BaseModel


class PatentScheme(BaseModel):
    id: int  
    publication_number: str
    title: str
    ai_summary: str
    raw_source_url: str
    assignee: str
    inventors: dict[str, str]
    priority_date: str
    application_date: str
    grant_date: str
    jurisdictions: str
    classifications: dict[str, str]
    application_events: str
    citations: dict[str, str]
    image_urls: dict[str, str]
    landscapes: str
    publish_date: str
    citations_non_patent: str
    provenance: str
    attachment_urls: str