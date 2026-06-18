# AI Resume Analyzer & ATS Checker

An intelligent resume analysis tool that evaluates resumes against ATS (Applicant Tracking System) criteria, compares with job descriptions, and provides actionable improvement suggestions.

## Features

- **PDF Resume Parsing** - Extract text from PDF resumes with section detection
- **ATS Score Calculation** - Multi-factor scoring (keywords, formatting, education, experience, skills)
- **Missing Skills Identification** - Detect skills missing compared to job descriptions
- **Job Description Comparison** - Match resume against specific job requirements
- **AI-Powered Analysis** - Get intelligent suggestions and resume summaries
- **Improvement Suggestions** - Actionable recommendations to boost your ATS score

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** OpenAI / Gemini API
- **PDF Parsing:** PyPDF2
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Database:** SQLite

## Project Structure

```
ai-resume-analyzer/
├── app.py                         # FastAPI main application
├── models.py                      # Pydantic data models
├── database.py                    # SQLite database setup
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
├── services/
│   ├── parser_service.py          # PDF text extraction & section parsing
│   ├── ats_service.py             # ATS scoring algorithm (rule-based)
│   ├── ai_service.py              # AI-powered analysis with fallback
│   └── comparison_service.py      # Resume vs job description comparison
└── templates/
    └── index.html                 # Frontend interface
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables (optional - works without AI too)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

The ATS scoring works fully without an API key. AI features (smart suggestions, summary) enhance the output.

### 4. Run the application

```bash
python app.py
```

or

```bash
uvicorn app:app --reload
```

### 5. Open in browser

Navigate to: `http://localhost:8000`

## Project Flow

1. **Upload Resume** → Upload a PDF resume file
2. **Enter Job Description** → (Optional) Paste the job description for comparison
3. **Analyze** → Click analyze to get:
   - **ATS Score** (0-100) with sub-scores for keywords, formatting, education, experience, skills
   - **Missing Skills** - Skills present in job description but missing from resume
   - **Improvement Suggestions** - Actionable tips to improve
   - **Resume Summary** - AI-generated summary of your resume
   - **Comparison Results** - Detailed match analysis

## ATS Scoring Criteria

| Factor | Weight | Description |
|--------|--------|-------------|
| Keyword Match | 30% | Relevance of skills and terms to job description |
| Formatting | 20% | Section headers, bullet points, structure |
| Education | 15% | Degree details, certifications |
| Experience | 20% | Years of experience, job titles, achievements |
| Skills | 15% | Technical and soft skills listed |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend interface |
| POST | `/api/resume/upload` | Upload a PDF resume |
| POST | `/api/resume/analyze` | Analyze resume (optional job description) |
| GET | `/api/resume/{id}/score` | Get ATS score for a resume |
| POST | `/api/resume/{id}/improve` | Get improvement suggestions |
| GET | `/api/resumes` | List all uploaded resumes |
| GET | `/api/resume/{id}` | Get resume details |
