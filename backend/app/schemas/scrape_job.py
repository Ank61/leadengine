from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class ScrapeJobCreate(BaseModel):
    """Schema for creating a new scrape job"""
    user_id: UUID = Field(..., description="ID of the user creating the job")
    
    # Scrape criteria
    industry: Optional[str] = Field(None, description="Target industry (e.g., 'SaaS', 'Healthcare', 'Finance')")
    geography: Optional[str] = Field(None, description="Target geography/location (e.g., 'Sydney', 'Australia', 'North America')")
    keywords: Optional[list[str]] = Field(default_factory=list, description="List of keywords to search for")
    source_types: Optional[list[str]] = Field(default_factory=list, description="List of sources to scrape (e.g., ['google', 'linkedin'])")
    
    search_query: str = Field(..., description="Main search query for scraping")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters for scraping")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "industry": "SaaS",
                "geography": "Sydney, Australia",
                "keywords": ["B2B", "enterprise", "cloud"],
                "source_types": ["google", "linkedin"],
                "search_query": "saas companies sydney",
                "filters": {
                    "company_size": "50-200",
                    "revenue": ">1M"
                }
            }
        }


class ScrapeJobResponse(BaseModel):
    """Schema for scrape job response"""
    job_id: UUID
    user_id: UUID
    status: str
    
    # Scrape criteria
    industry: Optional[str]
    geography: Optional[str]
    keywords: Optional[list[str]]
    source_types: Optional[list[str]]
    search_query: str
    filters: Optional[Dict[str, Any]]
    
    total_found: int
    total_processed: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ScrapeJobStatusResponse(BaseModel):
    """Schema for job status check"""
    job_id: UUID
    status: str
    total_found: int
    total_processed: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
