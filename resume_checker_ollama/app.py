from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # or "mistral" or any model you have

def extract_salary_ollama(job_text):
    prompt = (
        "Based on the following job description, extract the estimated salary or salary range. "
        " Do not include any other information, just the salary or range.\n\n"
        "If no salary is mentioned, reply with 'Salary Not specified'.\n\n"
        f"Job Description:\n{job_text}\n\nSalary:"
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60
    )
    if response.ok:
        result = response.json()
        salary = result.get("response", "").strip()
        return salary
    return "Not specified"

def extract_soft_skills_ollama(job_text):
    prompt = (
        "Extract a comma-separated list of soft skills required for this position, "
        "such as communication, teamwork, leadership, problem solving, adaptability, etc. "
        "Only list the keywords, no explanations. Do not include technical skills, salary, or benefits.\n\n"
        f"Job Description:\n{job_text}\n\nSoft Skills:"
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60
    )
    if response.ok:
        result = response.json()
        keywords = result.get("response", "")
        blacklist = [
            "here is a comma-separated list of soft skills",
            "this",
        ]
        return [
            kw.strip().lower()
            for kw in keywords.split(",")
            if kw.strip() and kw.strip().lower() not in blacklist
        ]
    return []

def extract_keywords_ollama(job_text):
    prompt = (
        "Extract a comma-separated list of technical skills and tools, programming languages, "
        "frameworks, and tools required for this position. Only list the keywords, no explanations.\n\n"
        "make sure you remove all explanations and only return the keywords.\n\n"
        "Do not include salary, benefits, or any other non-technical information.\n\n"
        f"Job Description:\n{job_text}\n\nKeywords:"
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60
    )
    if response.ok:
        result = response.json()
        keywords = result.get("response", "")
        # Remove unwanted phrases from the list
        blacklist = [
            "here is a comma-separated list of technical skills",
            "here is a list of technical skills and tools"
            "this",  # in case "this" also appears
        ]
        return [
            kw.strip().lower()
            for kw in keywords.split(",")
            if kw.strip() and kw.strip().lower() not in blacklist
        ]
    return []

def extract_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".pdf"):
        try:
            import PyPDF2
            file_storage.seek(0)
            reader = PyPDF2.PdfReader(file_storage)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception:
            return ""
    else:
        file_storage.seek(0)
        return file_storage.read().decode("utf-8", errors="ignore")

@app.route("/", methods=["GET", "POST"])
def home():
    keywords = []
    resume_text = ""
    job_text = ""
    comparison = []
    if request.method == "POST":
        job_text = request.form.get("job_text", "")
        resume_text = request.form.get("resume_text", "")
        resume_file = request.files.get("resume_file")
        if resume_file and resume_file.filename:
            resume_text = extract_text_from_file(resume_file)
        # Extract keywords using Ollama
        if job_text:
            print('JOB TEXT', job_text[:100])
            keywords = extract_keywords_ollama(job_text)
            salary = extract_salary_ollama(job_text)
            soft_skills = extract_soft_skills_ollama(job_text)
        # Compare
        resume_text_lower = resume_text.lower()
        comparison = [
            {"keyword": kw, "in_resume": kw in resume_text_lower}
            for kw in keywords
        ]
    return render_template(
        "home.html",
        job_text=job_text,
        resume_text=resume_text,
        comparison=comparison,
        keywords=keywords,salary=salary,soft_skills=soft_skills,
    )

if __name__ == "__main__":
    app.run(debug=True)