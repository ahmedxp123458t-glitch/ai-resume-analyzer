import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.sep, "tmp", "resumes.db")


def get_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_PATH)


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            overall_score REAL,
            keyword_score REAL,
            formatting_score REAL,
            education_score REAL,
            experience_score REAL,
            skills_score REAL,
            keyword_details TEXT,
            formatting_details TEXT,
            missing_critical_skills TEXT,
            improvement_suggestions TEXT,
            resume_summary TEXT,
            comparison_results TEXT,
            job_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    """)
    conn.commit()
    conn.close()


def save_resume(filename: str, raw_text: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (filename, raw_text) VALUES (?, ?)",
        (filename, raw_text),
    )
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id


def get_resume(resume_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_resumes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_analysis(resume_id: int, analysis_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_results
        (resume_id, overall_score, keyword_score, formatting_score,
         education_score, experience_score, skills_score,
         keyword_details, formatting_details, missing_critical_skills,
         improvement_suggestions, resume_summary, comparison_results,
         job_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resume_id,
        analysis_data.get("overall_score"),
        analysis_data.get("keyword_score"),
        analysis_data.get("formatting_score"),
        analysis_data.get("education_score"),
        analysis_data.get("experience_score"),
        analysis_data.get("skills_score"),
        analysis_data.get("keyword_details"),
        analysis_data.get("formatting_details"),
        analysis_data.get("missing_critical_skills"),
        analysis_data.get("improvement_suggestions"),
        analysis_data.get("resume_summary"),
        analysis_data.get("comparison_results"),
        analysis_data.get("job_description"),
    ))
    conn.commit()
    conn.close()


def get_analysis(resume_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analysis_results WHERE resume_id = ? ORDER BY created_at DESC LIMIT 1",
        (resume_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
