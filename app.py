import os
import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from dotenv import load_dotenv

load_dotenv()

from database import init_db, save_resume, get_resume, get_all_resumes, save_analysis, get_analysis
from models import (
    ResumeUploadResponse,
    ATSScoreResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ImproveResponse,
    ComparisonResult,
)
from services.parser_service import extract_text_from_pdf, clean_text, extract_sections
from services.ats_service import analyze as ats_analyze
from services.ai_service import analyze_with_ai, is_ai_available, generate_improvement_suggestions, generate_resume_summary
from services.comparison_service import compare as compare_resume_jd

app = FastAPI(title="AI Resume Analyzer & ATS Checker")


@app.on_event("startup")
async def startup():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    init_db()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = Path(os.path.sep) / "tmp" / "uploads"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def json_serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    return str(obj)


@app.post("/api/resume/upload", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        file_bytes = await file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        cleaned_text = clean_text(raw_text)

        if not cleaned_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        resume_id = save_resume(file.filename, cleaned_text)
        sections = extract_sections(cleaned_text)

        return {
            "id": resume_id,
            "filename": file.filename,
            "text_length": len(cleaned_text),
            "sections": {k: len(v) for k, v in sections.items() if v},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@app.post("/api/resume/analyze", response_model=dict)
async def analyze_resume(request_data: AnalyzeRequest):
    resume = get_resume(request_data.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job_description = request_data.job_description

    ats_results = ats_analyze(resume["raw_text"], job_description)

    ai_results = analyze_with_ai(resume["raw_text"], job_description)

    suggestions = ai_results.get("suggestions", [])
    if not suggestions:
        suggestions = _generate_rule_based_suggestions(resume["raw_text"], ats_results)

    summary = ai_results.get("summary", "")
    if not summary:
        summary = generate_resume_summary(resume["raw_text"])

    comparison_results = None
    if job_description:
        comparison_results = compare_resume_jd(resume["raw_text"], job_description)

    missing_skills = list(set(
        ats_results.get("missing_critical_skills", []) +
        (comparison_results.get("missing_skills", []) if comparison_results else [])
    ))

    analysis_data = {
        "overall_score": ats_results["overall_score"],
        "keyword_score": ats_results["keyword_score"],
        "formatting_score": ats_results["formatting_score"],
        "education_score": ats_results["education_score"],
        "experience_score": ats_results["experience_score"],
        "skills_score": ats_results["skills_score"],
        "keyword_details": json.dumps(ats_results["keyword_details"], default=json_serialize),
        "formatting_details": json.dumps(ats_results["formatting_details"], default=json_serialize),
        "missing_critical_skills": json.dumps(missing_skills, default=json_serialize),
        "improvement_suggestions": json.dumps(suggestions, default=json_serialize),
        "resume_summary": summary,
        "comparison_results": json.dumps(comparison_results, default=json_serialize) if comparison_results else None,
        "job_description": job_description,
    }
    save_analysis(request_data.resume_id, analysis_data)

    ats_score_response = {
        "resume_id": request_data.resume_id,
        "overall_score": ats_results["overall_score"],
        "keyword_score": ats_results["keyword_score"],
        "formatting_score": ats_results["formatting_score"],
        "education_score": ats_results["education_score"],
        "experience_score": ats_results["experience_score"],
        "skills_score": ats_results["skills_score"],
        "keyword_details": ats_results["keyword_details"],
        "formatting_details": ats_results["formatting_details"],
        "missing_critical_skills": missing_skills,
    }

    return {
        "resume_id": request_data.resume_id,
        "ats_score": ats_score_response,
        "missing_skills": missing_skills,
        "improvement_suggestions": suggestions,
        "resume_summary": summary,
        "comparison_results": comparison_results,
    }


@app.get("/api/resume/{resume_id}/score", response_model=dict)
async def get_score(resume_id: int):
    resume = get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    analysis = get_analysis(resume_id)
    if analysis:
        return {
            "resume_id": resume_id,
            "overall_score": analysis["overall_score"],
            "keyword_score": analysis["keyword_score"],
            "formatting_score": analysis["formatting_score"],
            "education_score": analysis["education_score"],
            "experience_score": analysis["experience_score"],
            "skills_score": analysis["skills_score"],
            "keyword_details": json.loads(analysis["keyword_details"]) if analysis["keyword_details"] else {},
            "formatting_details": json.loads(analysis["formatting_details"]) if analysis["formatting_details"] else {},
            "missing_critical_skills": json.loads(analysis["missing_critical_skills"]) if analysis["missing_critical_skills"] else [],
        }

    ats_results = ats_analyze(resume["raw_text"])
    return {
        "resume_id": resume_id,
        "overall_score": ats_results["overall_score"],
        "keyword_score": ats_results["keyword_score"],
        "formatting_score": ats_results["formatting_score"],
        "education_score": ats_results["education_score"],
        "experience_score": ats_results["experience_score"],
        "skills_score": ats_results["skills_score"],
        "keyword_details": ats_results["keyword_details"],
        "formatting_details": ats_results["formatting_details"],
        "missing_critical_skills": ats_results["missing_critical_skills"],
    }


@app.post("/api/resume/{resume_id}/improve", response_model=dict)
async def improve_resume(resume_id: int, request_data: dict = None):
    resume = get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job_description = None
    if request_data:
        job_description = request_data.get("job_description")

    suggestions = generate_improvement_suggestions(resume["raw_text"], job_description)
    if not suggestions:
        ats_results = ats_analyze(resume["raw_text"], job_description)
        suggestions = _generate_rule_based_suggestions(resume["raw_text"], ats_results)

    priority = "high" if len(suggestions) > 5 else "medium" if len(suggestions) > 2 else "low"

    return {
        "resume_id": resume_id,
        "suggestions": suggestions,
        "priority": priority,
    }


@app.get("/api/resumes", response_model=list)
async def list_resumes():
    resumes = get_all_resumes()
    return [
        {"id": r["id"], "filename": r["filename"], "created_at": r["created_at"]}
        for r in resumes
    ]


@app.get("/api/resume/{resume_id}", response_model=dict)
async def get_resume_details(resume_id: int):
    resume = get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    sections = extract_sections(resume["raw_text"])
    return {
        "id": resume["id"],
        "filename": resume["filename"],
        "raw_text": resume["raw_text"],
        "sections": sections,
        "created_at": resume["created_at"],
    }


def _generate_rule_based_suggestions(text: str, ats_results: dict) -> list:
    suggestions = []
    text_lower = text.lower()

    sections_missing = ats_results.get("formatting_details", {}).get("sections_missing", [])
    if sections_missing:
        for sec in sections_missing:
            suggestions.append(f"Add a '{sec.title()}' section to your resume")

    if "summary" not in text_lower and "profile" not in text_lower:
        suggestions.append("Add a professional summary/profile section at the top")

    if ats_results.get("skills_score", 100) < 40:
        suggestions.append("List more technical skills relevant to your field")

    bullet_points = text.count("\n-") + text.count("\n•") + text.count("\n*")
    if bullet_points < 3:
        suggestions.append("Use bullet points to highlight achievements and responsibilities")

    numbers = sum(c.isdigit() for c in text)
    if numbers < 10:
        suggestions.append("Add quantifiable achievements (numbers, percentages, metrics)")

    if ats_results.get("keyword_score", 100) < 60:
        suggestions.append("Include more industry keywords from the job description")

    ats_score = ats_results.get("overall_score", 0)
    if ats_score < 50:
        suggestions.append("Consider reformatting your resume with clear section headers")
        suggestions.append("Use action verbs like 'Led', 'Developed', 'Implemented'")

    if not suggestions:
        suggestions.append("Your resume looks good! Consider tailoring it for specific roles")

    return suggestions
