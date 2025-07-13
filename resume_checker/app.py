from flask import Flask, render_template, request
import os
import re
import spacy

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)

COMMON_SKILLS = [
    "python", "java", "sql", "excel", "project management", "data analysis",
    "communication", "leadership", "machine learning", "aws", "azure",
    "c++", "javascript", "react", "django", "flask", "tableau", "power bi",
    "git", "linux", "docker", "kubernetes", "problem solving"
]

TECHNICAL_SKILLS = ['analytics', 'big data', 'cloud computing', 'data visualization'
    "python", "java", "sql", "excel", "project management", "data analysis",
    "machine learning", "aws", "azure", "c++", "javascript", "react", "django",
    "flask", "tableau", "power bi", "git", "linux", "docker", "kubernetes",
    "html", "css", "typescript", "node.js", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "spark", "hadoop", "bash", "shell", "matlab",
    "r", "sas", "jira", "confluence", "agile", "scrum", "rest", "graphql",
    "api", "ci/cd", "devops", "cloud", "gcp", "bigquery", "airflow"
]
# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_relevant_keywords_nlp(job_text):
    doc = nlp(job_text)
    # Extract noun chunks and proper nouns as candidate keywords
    keywords = set()
    for chunk in doc.noun_chunks:
        kw = chunk.text.strip().lower()
        if len(kw) > 2 and kw in TECHNICAL_SKILLS:
            keywords.add(kw)
    for token in doc:
        kw = token.text.strip().lower()
        if token.pos_ in {"PROPN", "NOUN"} and len(kw) > 2 and kw in TECHNICAL_SKILLS:
            keywords.add(kw)
    # Also match technical skills directly in the job text
    job_text_lower = job_text.lower()
    for skill in TECHNICAL_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', job_text_lower):
            keywords.add(skill)
    return list(keywords)


def extract_text_from_pdf(pdf_file):
    if not PyPDF2:
        print('NO LIBRARY')
        return ""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    print('EXTRACTED TEXT')
    return text

def extract_relevant_keywords(job_text):
    job_text_lower = job_text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', job_text_lower):
            found_skills.append(skill)
    return found_skills

@app.route("/", methods=["GET", "POST"])
def home():
    missing_keywords = None
    resume_text = ""
    job_text = ""
    relevant_keywords = ""
    if request.method == "POST":
        job_text = request.form.get("job_text", "")
        print('JOB TEXT', job_text[:100])
        relevant_keywords = request.form.get("relevant_keywords", "").strip()
        print('RELEVANT KEYWORDS', relevant_keywords)
        resume_file = request.files.get("resume_file")
        resume_text = request.form.get("resume_text", "")
        print('RESUME TEXT1', resume_file)
        # Extract resume text from file if uploaded
        if resume_file and resume_file.filename:
            if resume_file.filename.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(resume_file)
                print('RESUME TEXT2')
            else:
                resume_text = resume_file.read().decode("utf-8", errors="ignore")

        # Extract or parse relevant keywords
        if not relevant_keywords and job_text:
            print('EXTRACTING RELEVANT KEYWORDS')
            relevant_keywords_list = extract_relevant_keywords_nlp(job_text)
            relevant_keywords = ", ".join(relevant_keywords_list)
        else:
            print('EXTRACTING RELEVANT KEYWORDS2')
            relevant_keywords_list = [kw.strip().lower() for kw in relevant_keywords.split(",") if kw.strip()]
        print('RELEVANT KEYWORDS LIST', relevant_keywords_list)
        # Compare keywords to resume
        resume_text_lower = resume_text.lower()
        missing_keywords = [kw for kw in relevant_keywords_list if kw and kw not in resume_text_lower]

    return render_template(
        "home.html",
        missing_keywords=missing_keywords,
        resume_text=resume_text,
        job_text=job_text,
        relevant_keywords=relevant_keywords
    )

if __name__ == "__main__":
    app.run(debug=True)