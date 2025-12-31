"""Resume Parser Baseline Service.

This baseline uses simple keyword matching.
Students will replace this with NLP/NER models.
"""
import re
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Resume Parser Service (Baseline)",
    description="Extracts skills via keyword matching - no NLP",
    version="1.0.0"
)

# Predefined skill keywords
SKILL_KEYWORDS = [
    "python", "javascript", "java", "c++", "c#", "go", "rust", "ruby",
    "typescript", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "pandas", "numpy", "scikit-learn", "spark", "hadoop",
    "git", "ci/cd", "jenkins", "github actions",
    "agile", "scrum", "jira", "project management",
    "html", "css", "sass", "tailwind",
    "rest api", "graphql", "microservices",
    "linux", "bash", "shell scripting"
]


class ParseRequest(BaseModel):
    resume_text: str
    resume_format: Optional[str] = "text"


class ParseResponse(BaseModel):
    skills: List[str]
    experience_years: int
    education: Dict[str, Any]
    work_history: List[Dict[str, Any]]
    summary: str
    baseline: bool = True
    method: str = "keyword_matching"


@app.get("/")
async def root():
    return {"service": "resume_parser", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "resume_parser"}


@app.post("/parse", response_model=ParseResponse)
async def parse(request: ParseRequest):
    """
    Baseline parsing: keyword matching for skills.

    In a real implementation, this would:
    1. Use NER to extract entities (skills, companies, degrees)
    2. Use text classification for sections
    3. Use embeddings for semantic skill matching
    """
    text = request.resume_text.lower()

    # Find matching skills
    found_skills = []
    for skill in SKILL_KEYWORDS:
        if skill in text:
            found_skills.append(skill.title())

    # Simple pattern for years of experience
    experience_years = 0
    year_patterns = re.findall(r'(\d+)\+?\s*years?', text)
    if year_patterns:
        experience_years = max(int(y) for y in year_patterns)

    # Create summary from first 200 chars
    summary = request.resume_text[:200].strip()
    if len(request.resume_text) > 200:
        summary += "..."

    return ParseResponse(
        skills=found_skills,
        experience_years=experience_years,
        education={},
        work_history=[],
        summary=summary,
        baseline=True,
        method="keyword_matching"
    )
