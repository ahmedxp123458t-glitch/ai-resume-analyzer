from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    text_length: int
    created_at: datetime


class ResumeResponse(BaseModel):
    id: int
    filename: str
    raw_text: str
    created_at: datetime


class ATSScoreResponse(BaseModel):
    resume_id: int
    overall_score: float
    keyword_score: float
    formatting_score: float
    education_score: float
    experience_score: float
    skills_score: float
    keyword_details: dict
    formatting_details: dict
    missing_critical_skills: List[str]


class AnalyzeRequest(BaseModel):
    resume_id: int
    job_description: Optional[str] = None


class AnalyzeResponse(BaseModel):
    resume_id: int
    ats_score: ATSScoreResponse
    missing_skills: List[str]
    improvement_suggestions: List[str]
    resume_summary: str
    comparison_results: Optional[dict] = None


class ImproveRequest(BaseModel):
    job_description: Optional[str] = None


class ImproveResponse(BaseModel):
    resume_id: int
    suggestions: List[str]
    priority: str


class ComparisonResult(BaseModel):
    matching_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    match_percentage: float
    job_requirements_met: dict
    format: Optional[str] = None


class ResumeSummary(BaseModel):
    summary: str
    key_skills: List[str]
    experience_years: Optional[float] = None
    education: Optional[str] = None
