import requests
import json 

class GenAIInteractor:
    def __init__(self, job_text, resume_text, model="llama3.2:latest",  url="http://localhost:11434/api/generate", temperature = 0.2, top_p=0.2):
        self.job_text = job_text
        self.resume_text = resume_text
        self.model = model
        self.url = url
        self.model_temperature = temperature
        self.model_top_p = top_p
        self.timeout = 120

    def run_genai(self, prompt):
        response = requests.post(
            self.url,
            json = {"model": self.model, 
                    "prompt": prompt, 
                    "stream": False, 
                    "temperature": self.model_temperature, 
                    "top_p":self.model_top_p
                    },
            timeout=self.timeout
        )
        return response.ok, response.json().get("response", "")
    
    def compare_keywords_ollama(self, keywords, text):
        if not keywords:
            return []
        prompt = (
            "Given the following list of technical skills and the resume text, "
            "return a JSON array of objects, each with 'keyword' and 'in_resume' (true/false), "
            "indicating if the skill is present in the resume. "
            "Only use the keywords provided, and do not add explanations.\n\n"
            f"Keywords: {', '.join(keywords)}\n\n"
            f"Resume:\n{text}\n\n"
            "Output:"
        )
        response_status, result = self.run_genai(prompt)
        if response_status:
            try:
                # Find the first JSON array in the response
                start = result.find('[')
                end = result.rfind(']')
                if start != -1 and end != -1:
                    return json.loads(result[start:end+1])
            except Exception as E:
                print("Error parsing JSON from Ollama response", str(E))
                pass
        else: 
            return [{"keyword": kw, "in_resume": kw in self.resume_text.lower()} for kw in self.keywords]
    
    def extract_salary_ollama(self):
        prompt = (
            "Based on the following job description, extract the estimated salary or salary range. "
            " Do not include any other information, just the salary or range.\n\n"
            "If no salary is mentioned, reply with 'Salary Not specified'.\n\n"
            f"Job Description:\n{self.job_text}\n\nSalary:"
        )
        response_status, result = self.run_genai(prompt)
        if response_status:
            self.salary =  result.strip()
        else:
            self.salary =  "Not specified"
    
    def extract_soft_skills_ollama(self):
        prompt = (
            "Based on the following job description, extract a list of soft skills required for the role. "
            " Return only a comma-separated list of skills without any additional text.\n\n"
            f"Job Description:\n{self.job_text}\n\nSoft Skills:"
        )
        response_status, result = self.run_genai(prompt)
        if response_status:
            skills_text = result.strip()
            # Split by commas and clean up whitespace
            self.skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
        else:
            self.skills = []
    
    def extract_keywords_ollama(self):
        prompt = (
            "Extract a comma-separated list of technical skills and tools required for this position, "
            "such as programming languages, frameworks, software, platforms, etc. "
            "Only list the keywords, no explanations. Do not include soft skills, salary, or benefits.\n\n"
            f"Job Description:\n{self.job_text}\n\nTechnical Skills and Tools:"
        )
        response_status, result = self.run_genai(prompt)
        if response_status:
            keywords = result
            # Split by commas and clean up whitespace
            self.keywords_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        else:
            self.keywords_list = []
    
    def run_process(self):
        self.extract_keywords_ollama()
        self.extract_salary_ollama()
        self.extract_soft_skills_ollama()
        self.comparison = self.compare_keywords_ollama(self.keywords_list, self.resume_text)
        self.soft_comparison = self.compare_keywords_ollama(self.skills, self.resume_text)
        return self.comparison, self.soft_comparison, self.salary

    @staticmethod
    def extract_text_from_file(file_storage):
        filename = file_storage.filename.lower()
        print('FILENAME', filename)
        if filename.endswith(".pdf"):
            try:
                import PyPDF2
                file_storage.seek(0)
                reader = PyPDF2.PdfReader(file_storage)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as E:
                print(str(E))
                print("There is an error reading the PDF file.")
                return ""
        else:
            file_storage.seek(0)
            return file_storage.read().decode("utf-8", errors="ignore")