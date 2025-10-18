from flask import Flask, render_template, request
from functions.genai_interactor import GenAIInteractor

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    resume_text = job_text = ''  
    soft_comparison = salary = None
    comparison = None
    if request.method == "POST":
        # Capture the resume information from text area of file upload
        job_text = request.form.get("job_text", None)
        resume_text = request.form.get("resume_text", None)
        resume_file = request.files.get("resume_file", None)
        if resume_file: 
            resume_text = GenAIInteractor.extract_text_from_file(resume_file)
            print('RESUME TEXT FROM PDF', resume_text)
        if job_text and resume_text:
            print('JOB TEXT', job_text[:100])
            GenAIInteractor_Instance = GenAIInteractor(job_text, resume_text)
            comparison,soft_comparison, salary = GenAIInteractor_Instance.run_process()
            # comparison = GenAIInteractor_Instance.comparison
            # soft_comparison = GenAIInteractor_Instance.soft_comparison
            # salary=GenAIInteractor_Instance.salary
    return render_template(
        "home.html",
        job_text=job_text,
        resume_text=resume_text,
        comparison=comparison,
        salary=salary,
        soft_comparison=soft_comparison,
    )

if __name__ == "__main__":
    app.run(debug=True)