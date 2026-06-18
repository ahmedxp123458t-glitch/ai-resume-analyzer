import re
from typing import List, Optional

from .ats_service import extract_keywords

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
    "git", "github", "gitlab", "ci/cd", "devops",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
    "html", "css", "bootstrap", "tailwind", "sass",
    "rest api", "graphql", "microservices", "api",
    "agile", "scrum", "jira", "confluence",
    "leadership", "communication", "teamwork", "problem solving",
    "data analysis", "data science", "data engineering", "big data",
    "spark", "hadoop", "kafka", "airflow",
    "linux", "unix", "bash", "powershell",
    "excel", "word", "powerpoint", "outlook",
    "project management", "product management", "business analysis",
    "docker", "kubernetes", "jenkins", "ansible", "puppet", "chef",
    "swift", "kotlin", "dart", "flutter", "react native",
    "selenium", "cypress", "jest", "mocha", "chai",
    "figma", "sketch", "adobe xd", "photoshop", "illustrator",
]

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability",
    "creativity", "collaboration", "analytical", "organization",
    "mentoring", "presentation", "negotiation", "conflict resolution",
]


def extract_keywords_from_jd(job_description: str) -> List[str]:
    jd_lower = job_description.lower()
    found = set()
    for skill in COMMON_SKILLS:
        if skill in jd_lower:
            found.add(skill)
    for skill in SOFT_SKILLS:
        if skill in jd_lower:
            found.add(skill)

    degree_patterns = re.findall(
        r"(bachelor|master|phd|doctorate|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech|mba)",
        jd_lower,
    )
    for d in degree_patterns:
        found.add(d + " degree")

    years_req = re.findall(r'(\d+)\+?\s*(?:year|yr)', jd_lower)
    if years_req:
        found.add(f"{max(int(y) for y in years_req)}+ years experience")

    return sorted(found)


def compare(resume_text: str, job_description: str) -> dict:
    resume_lower = resume_text.lower()
    jd_keywords = extract_keywords_from_jd(job_description)

    matching_skills = []
    missing_skills = []
    extra_skills = []

    resume_skills = set(extract_keywords(resume_text))
    resume_skills_lower = {s.lower() for s in resume_skills}

    for skill in jd_keywords:
        if skill in resume_lower:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    for skill in resume_skills:
        if skill.lower() not in [s.lower() for s in jd_keywords]:
            extra_skills.append(skill)

    match_percentage = 0
    if jd_keywords:
        match_percentage = round((len(matching_skills) / len(jd_keywords)) * 100, 1)
    elif resume_skills:
        match_percentage = 50.0

    requirements_met = {}
    for skill in jd_keywords[:15]:
        requirements_met[skill] = skill in matching_skills

    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "match_percentage": match_percentage,
        "job_requirements_met": requirements_met,
    }
