import re
import math
from typing import List, Tuple, Optional

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
]

FORMATTING_KEYWORDS = [
    "education", "experience", "skills", "summary", "profile",
    "projects", "certifications", "contact", "references",
]

SECTIONS_EXPECTED = ["education", "experience", "skills"]


def extract_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found.add(skill)
    return sorted(found)


def calculate_keyword_score(text: str, job_description: Optional[str] = None) -> Tuple[float, dict]:
    text_lower = text.lower()
    details = {"matched_skills": [], "missing_skills": [], "total_keywords_checked": 0}

    if job_description:
        jd_lower = job_description.lower()
        jd_keywords = set()
        for skill in COMMON_SKILLS:
            if skill in jd_lower:
                jd_keywords.add(skill)
        details["total_keywords_checked"] = len(jd_keywords)

        matched = []
        missing = []
        for skill in jd_keywords:
            if skill in text_lower:
                matched.append(skill)
            else:
                missing.append(skill)
        details["matched_skills"] = matched
        details["missing_skills"] = missing

        if jd_keywords:
            score = (len(matched) / len(jd_keywords)) * 100
        else:
            score = 50.0
    else:
        skills_found = extract_keywords(text)
        details["matched_skills"] = skills_found
        details["total_keywords_checked"] = len(COMMON_SKILLS)
        if skills_found:
            score = min(100, (len(skills_found) / max(1, len(COMMON_SKILLS) * 0.3)) * 100)
        else:
            score = 10.0

    return round(min(100, score), 1), details


def calculate_formatting_score(text: str) -> Tuple[float, dict]:
    score = 100.0
    details = {"issues": [], "sections_found": [], "sections_missing": []}

    text_lower = text.lower()
    sections_found = []
    sections_missing = []

    for section in SECTIONS_EXPECTED:
        if section in text_lower:
            sections_found.append(section)
        else:
            sections_missing.append(section)

    details["sections_found"] = sections_found
    details["sections_missing"] = sections_missing

    if len(sections_missing) > 0:
        missing_pct = (len(sections_missing) / len(SECTIONS_EXPECTED)) * 100
        score -= missing_pct * 15
        details["issues"].append(f"Missing sections: {', '.join(sections_missing)}")

    lines = text.strip().split("\n")
    if len(lines) < 10:
        score -= 20
        details["issues"].append("Resume is too short")

    bullet_points = len(re.findall(r'[•\-*]\s', text))
    if bullet_points == 0:
        score -= 10
        details["issues"].append("No bullet points found (use • or - for achievements)")

    numbers = len(re.findall(r'\d+', text))
    if numbers < 5:
        score -= 10
        details["issues"].append("Few quantifiable achievements (use numbers to show impact)")

    char_count = len(text)
    if char_count < 500:
        score -= 15
        details["issues"].append("Resume content is too sparse")
    elif char_count > 10000:
        score -= 5
        details["issues"].append("Resume may be too long")

    emails = len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    if emails == 0:
        score -= 5
        details["issues"].append("No email address found")

    phones = len(re.findall(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text))
    if phones == 0:
        score -= 5
        details["issues"].append("No phone number found")

    score = max(0, min(100, score))
    return round(score, 1), details


def calculate_education_score(text: str) -> float:
    text_lower = text.lower()
    education_indicators = [
        "bachelor", "master", "phd", "doctorate", "b.s.", "m.s.", "b.a.", "m.a.",
        "b.tech", "m.tech", "degree", "university", "college", "school",
        "bachelor's", "master's", "ph.d", "mba", "bsc", "msc", "be ", "me ",
        "b.e.", "m.e.", "b.com", "m.com", "bachelor of", "master of",
    ]

    score = 0
    found_indicators = [ind for ind in education_indicators if ind in text_lower]
    if found_indicators:
        score = min(100, len(found_indicators) * 15)
    else:
        score = 10

    return round(min(100, score), 1)


def calculate_experience_score(text: str) -> float:
    text_lower = text.lower()
    experience_indicators = [
        "experience", "work", "employment", "job", "position", "role",
        "years", "managed", "led", "developed", "created", "implemented",
    ]

    found_indicators = [ind for ind in experience_indicators if ind in text_lower]
    experience_pct = len(found_indicators) / len(experience_indicators)

    years_exp = re.findall(r'(\d+)\+?\s*years?', text_lower)
    if years_exp:
        years = max(int(y) for y in years_exp)
        exp_score = min(100, years * 10)
    else:
        exp_score = 30 if experience_pct > 0.3 else 10

    score = (experience_pct * 50) + (exp_score * 0.5)
    return round(min(100, score), 1)


def calculate_skills_score(text: str) -> float:
    skills_found = extract_keywords(text)
    if not skills_found:
        return 5.0
    score = min(100, len(skills_found) * 5)
    return round(score, 1)


def calculate_overall_score(scores: dict) -> float:
    weights = {
        "keyword_score": 0.30,
        "formatting_score": 0.20,
        "education_score": 0.15,
        "experience_score": 0.20,
        "skills_score": 0.15,
    }
    total = 0
    for key, weight in weights.items():
        total += scores.get(key, 0) * weight
    return round(total, 1)


def analyze(text: str, job_description: Optional[str] = None) -> dict:
    keyword_score, keyword_details = calculate_keyword_score(text, job_description)
    formatting_score, formatting_details = calculate_formatting_score(text)
    education_score = calculate_education_score(text)
    experience_score = calculate_experience_score(text)
    skills_score_value = calculate_skills_score(text)

    scores = {
        "keyword_score": keyword_score,
        "formatting_score": formatting_score,
        "education_score": education_score,
        "experience_score": experience_score,
        "skills_score": skills_score_value,
    }

    overall_score = calculate_overall_score(scores)

    return {
        "overall_score": overall_score,
        **scores,
        "keyword_details": keyword_details,
        "formatting_details": formatting_details,
        "missing_critical_skills": keyword_details.get("missing_skills", []),
    }
