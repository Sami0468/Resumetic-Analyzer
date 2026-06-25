import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skill_extractor import extract_skills, extract_jd_skills

EXPERIENCE_KEYWORDS = [
    'experience', 'years', 'yr', 'yrs', 'worked', 'developed', 'managed',
    'led', 'built', 'designed', 'implemented', 'maintained', 'senior',
    'junior', 'intern', 'position', 'role', 'responsible'
]
EDUCATION_KEYWORDS = [
    'bachelor', 'master', 'phd', 'degree', 'university', 'college',
    'engineering', 'science', 'computer', 'bsc', 'msc', 'b.tech', 'm.tech',
    'b.e', 'm.e', 'diploma', 'graduate', 'undergraduate', 'cgpa', 'gpa'
]
FORMATTING_INDICATORS = [
    'objective', 'summary', 'experience', 'education', 'skills', 'projects',
    'achievements', 'certifications', 'awards', 'contact', 'email', 'phone'
]

def calculate_skill_score(resume_skills, jd_skills):
    if not jd_skills:
        return 50.0
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)
    if not jd_set:
        return 50.0
    match = len(resume_set & jd_set)
    return min(100.0, (match / len(jd_set)) * 100)

def calculate_experience_score(text):
    text_lower = text.lower()
    score = 0
    for kw in EXPERIENCE_KEYWORDS:
        if kw in text_lower:
            score += 1
    year_patterns = re.findall(r'\b\d{4}\b', text)
    if len(year_patterns) >= 2:
        score += 5
    return min(100.0, score * 8)

def calculate_education_score(text):
    text_lower = text.lower()
    score = 0
    for kw in EDUCATION_KEYWORDS:
        if kw in text_lower:
            score += 1
    return min(100.0, score * 15)

def calculate_formatting_score(text):
    text_lower = text.lower()
    score = 0
    for ind in FORMATTING_INDICATORS:
        if ind in text_lower:
            score += 1
    length_score = min(30, len(text.split()) / 10)
    return min(100.0, score * 6 + length_score)

def calculate_job_match(resume_text, jd_text):
    if not jd_text.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(sim * 100, 2)
    except:
        return 0.0

def calculate_ats_score(resume_text, jd_text=""):
    resume_skills_data = extract_skills(resume_text)
    resume_skills = resume_skills_data["all"]
    jd_skills = extract_jd_skills(jd_text) if jd_text else []

    skill_score = calculate_skill_score(resume_skills, jd_skills)
    exp_score = calculate_experience_score(resume_text)
    edu_score = calculate_education_score(resume_text)
    fmt_score = calculate_formatting_score(resume_text)

    # Weighted formula: 40% skill, 30% experience, 20% education, 10% format
    ats = (skill_score * 0.40) + (exp_score * 0.30) + (edu_score * 0.20) + (fmt_score * 0.10)
    ats = max(10.0, min(99.0, round(ats, 1)))

    job_match = calculate_job_match(resume_text, jd_text) if jd_text else 0.0

    missing_skills = []
    if jd_skills:
        resume_set = set(s.lower() for s in resume_skills)
        missing_skills = [s for s in jd_skills if s.lower() not in resume_set]

    suggestions = generate_suggestions(resume_text, resume_skills, missing_skills, ats)

    return {
        "ats_score": ats,
        "job_match": job_match,
        "skills_found": resume_skills,
        "technical_skills": resume_skills_data["technical"],
        "soft_skills": resume_skills_data["soft"],
        "missing_skills": missing_skills[:10],
        "suggestions": suggestions,
        "breakdown": {
            "skill_match": round(skill_score, 1),
            "experience": round(exp_score, 1),
            "education": round(edu_score, 1),
            "formatting": round(fmt_score, 1)
        }
    }

def generate_suggestions(text, skills, missing_skills, ats_score):
    suggestions = []
    text_lower = text.lower()

    if missing_skills:
        for skill in missing_skills[:3]:
            suggestions.append(f"Add {skill} to your skills section")

    if 'summary' not in text_lower and 'objective' not in text_lower:
        suggestions.append("Add a professional summary at the top of your resume")

    if 'project' not in text_lower:
        suggestions.append("Include a projects section to showcase your work")

    if len(text.split()) < 200:
        suggestions.append("Expand your resume with more detailed descriptions")

    if 'github' not in text_lower and 'linkedin' not in text_lower:
        suggestions.append("Add your GitHub/LinkedIn profile links")

    if 'certification' not in text_lower:
        suggestions.append("Add certifications to strengthen your profile")

    if ats_score < 60:
        suggestions.append("Use more keywords from the job description throughout your resume")

    if 'achievement' not in text_lower and 'accomplish' not in text_lower:
        suggestions.append("Quantify achievements with numbers and metrics (e.g., 'Improved performance by 30%')")

    return suggestions[:6]