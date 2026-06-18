import os
import json
import re
from typing import List, Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_ai_available = bool(OPENAI_API_KEY or GEMINI_API_KEY)


def is_ai_available() -> bool:
    return _ai_available


def _call_openai(prompt: str) -> Optional[str]:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def _call_gemini(prompt: str) -> Optional[str]:
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None


def _call_ai(prompt: str) -> Optional[str]:
    result = _call_openai(prompt)
    if result:
        return result
    result = _call_gemini(prompt)
    if result:
        return result
    return None


def extract_skills_with_ai(text: str) -> List[str]:
    prompt = f"""
    Extract all technical and professional skills from this resume text.
    Return them as a comma-separated list. Only return the list, nothing else.

    Resume:
    {text[:3000]}
    """

    result = _call_ai(prompt)
    if result:
        skills = [s.strip() for s in result.split(",") if s.strip()]
        return skills
    return []


def generate_improvement_suggestions(text: str, job_description: Optional[str] = None) -> List[str]:
    prompt = f"""
    Analyze this resume and provide specific, actionable improvement suggestions.
    Return 5-7 bullet points. Format as a numbered list.

    Resume:
    {text[:3000]}
    """

    if job_description:
        prompt += f"""
    Consider this job description:
    {job_description[:2000]}
    """

    result = _call_ai(prompt)
    if result:
        suggestions = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                clean = re.sub(r'^[\d\.\-\*\)\s]+', '', line).strip()
                if clean:
                    suggestions.append(clean)
        return suggestions[:7]
    return []


def generate_resume_summary(text: str) -> str:
    prompt = f"""
    Generate a concise professional summary (2-3 sentences) of this resume, 
    highlighting key skills, experience level, and career focus.

    Resume:
    {text[:3000]}
    """

    result = _call_ai(prompt)
    if result:
        return result.strip()
    return _generate_rule_based_summary(text)


def _generate_rule_based_summary(text: str) -> str:
    text_lower = text.lower()
    skills_found = []

    skill_categories = {
        "programming": ["python", "java", "javascript", "typescript", "c++", "go", "rust", "ruby"],
        "frontend": ["react", "angular", "vue", "html", "css"],
        "backend": ["django", "flask", "node.js", "spring", "express"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "data": ["machine learning", "data science", "data analysis", "nlp"],
    }

    for category, skills in skill_categories.items():
        found = [s for s in skills if s in text_lower]
        if found:
            skills_found.extend(found[:3])

    years = re.findall(r'(\d+)\+?\s*years?', text_lower)
    exp_text = ""
    if years:
        exp_text = f" with {max(int(y) for y in years)}+ years of experience"

    skills_text = ""
    if skills_found:
        unique_skills = list(set(skills_found))[:6]
        skills_text = f" Skilled in {', '.join(unique_skills)}."

    return f"Professional{exp_text} with expertise across multiple domains.{skills_text}"


def analyze_with_ai(text: str, job_description: Optional[str] = None) -> dict:
    if not _ai_available:
        return {}

    skills = extract_skills_with_ai(text)
    suggestions = generate_improvement_suggestions(text, job_description)
    summary = generate_resume_summary(text)

    return {
        "ai_skills": skills,
        "suggestions": suggestions,
        "summary": summary,
    }
