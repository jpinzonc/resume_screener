from flask import Flask, render_template, request
from functions.genai_interactor import GenAIInteractor, GenAIInteractorGoogle, extract_text_from_file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    new_resume = {}
    resume_text = job_text = ''  
    soft_comparison = salary = None
    comparison = None
    new_resume_format = {"Summary": "String", 
                         "Experience": "List_dictionary", 
                         "Skills": "Dictionary",
                         "Technical": "List_dictionary",
                         "Soft Skills": "List_dictionary",
                         "Education": "List_dictionary",
                         "Leadership": "String"
                         }

    if request.method == "POST":
        # Capture the resume information from text area of file upload
        job_text = request.form.get("job_text", None)
        resume_text = request.form.get("resume_text", None)
        resume_file = request.files.get("resume_file", None)
        google = False
        ollama = True
        if resume_file: 
            resume_text = extract_text_from_file(resume_file)
            print('RESUME TEXT FROM PDF', resume_text)
        if job_text and resume_text:
            print('JOB TEXT', job_text[:100])
            if ollama: 
                print('USING OLLAMA')
                GenAIInteractor_Instance = GenAIInteractor(job_text, resume_text)
            if google: # Google GEMINI
                print('USING GOOGLE GEMINI')
                import sys, os
                sys.path.append(os.path.abspath(os.path.join('../', 'secret')))
                from secret_info import google_genai_api
                GOOGLE_API_KEY = google_genai_api            
                GenAIInteractor_Instance = GenAIInteractorGoogle(GOOGLE_API_KEY, job_text, resume_text)

            comparison,soft_comparison, salary, new_resume= GenAIInteractor_Instance.run_process()
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
        new_resume = None if new_resume == {} else new_resume,
        new_resume_format = new_resume_format,
    )

if __name__ == "__main__":
    app.run(debug=True)