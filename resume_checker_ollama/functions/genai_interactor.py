import requests
import json 

class GenAIInteractor:
    def __init__(self, job_text, resume_text, model="qwen3:latest",
    # "llama3.2:latest", 
     url="http://localhost:11434/api/generate", temperature = 0.2, top_k=20, top_p=0.25):
        self.job_text = job_text
        self.resume_text = resume_text
        self.model = model
        self.url = url
        self.model_temperature = temperature
        self.model_top_k = top_k
        self.model_top_p = top_p
        self.timeout = 600

    def run_genai(self, prompt):
        response = requests.post(
            self.url,
            json = {"model": self.model, 
                    "prompt": prompt, 
                    "stream": False, 
                    "temperature": self.model_temperature, 
                    "top_k":self.model_top_k,
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
            "indicating if the skill is present in the resume. Make sure the skills are organize by in_resume true first."
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
            return []
    
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

    def convert_resume(self):
        prompt = (
            "You are an expert Human Resources agent working for a client that is looking for a job\n\n"
            f"This job descripion is a good opportunity {self.job_text} for your client.\n\n"
            f"Convert your clients resume {self.resume_text} to match the above description but highlight your clients expertise.\n\n"
            "Your response should ba a python dictionary where the keys correspond to the sections of the resume such as 'Summary', 'Experience', 'Skills', 'Education', 'Leadership'.\n\n"
            "and the values are the content for each section\n\n, "
            "The 'Summary' (an string) section should be a brief overview of the candidate's qualifications, experience, and career goals.\n\n" 
            "Make sure the 'Summary' aligns with the job description and highlights relevant experience and skills.\n\n"
            "The 'Experience' section should be a list of dictionaries, each dictionary representing a job with keys for 'Title', 'Company', 'Location', 'Duration', and 'Highlights'.\n\n"
            "All experiences must have 3 highlights and each must be a relevant achievement and quantifiable result that align with the job description.\n\n" 
            "The 'Skills' section should be a list of dictionaries with relevant skills extracted from the resume, and split into 'Technical' and 'Soft Skills'\n\n"
            "Each skill should be placed on its own dictionary with a key for 'Skill' and 'Proficiency Level' if available.\n\n"
            "The proficiency level can be Beginner, Intermediate, Advanced, Expert.\n\n"
            "If proficiency not available just leave it blank.\n\n"
            "Use all the skills in the resume, but sort them so that the most relevant skills to the job description are at the top of each list.\n\n"
            "The Education should be a list of dictionaries with keys for 'Degree', 'Institution'\n\n"
            "The 'Leadership' section should be an statement with highlights of leadership shown in the resume'.\n\n"
            "Do not include any information that is not relevant to the job description.\n\n"
            "Make sure to format the content in a way that is clear and easy to read.\n\n"
            "Provide the output as a JSON array of objects. Exclude any comments or explanations.\n\n"
            "In the output dictionary, add quotes before and after all squared parentheses to make it valid JSON.\n\n"
            "In all fields highlight the parts that match between job description and the resume.\n\n"
        )
        response_status, result = self.run_genai(prompt)
        if response_status:
            try:
                # Clean the response by finding the dictionary boundaries
                result = result.strip()
                start = result.find('{')
                end = result.rfind('}')
                if start != -1 and end != -1:
                    clean_result = result[start:end+1]
                    print('CLEAN RESULT', clean_result)
                    self.new_resume = json.loads(clean_result.strip().replace('\n', ""))
                else:
                    raise ValueError("No valid dictionary found in response")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing JSON: {e}")
                self.new_resume = "Error parsing response"
        else:
            self.new_resume = "Not specified"
    
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
            "Such as programming languages, frameworks, software, platforms, etc. "
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
        print("Extracting keywords...")
        self.extract_keywords_ollama()
        print("Extracting salary...")
        self.extract_salary_ollama()
        print("Extracting soft skills...")
        self.extract_soft_skills_ollama()
        print("Comparing keywords...")
        self.comparison = self.compare_keywords_ollama(self.keywords_list, self.resume_text)
        print("Comparing soft skills...")
        self.soft_comparison = self.compare_keywords_ollama(self.skills, self.resume_text)
        print("Converting resume...")
        self.convert_resume()
        print('DONE PROCESSING')
        return self.comparison, self.soft_comparison, self.salary, self.new_resume

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
        
from google.genai import Client, types, errors
import json

class GenAIInteractorGoogle:
    def __init__(self, GOOGLE_API_KEY, job_text, resume_text, model="gemini-2.5-flash", temperature = 0.2, top_k=20, top_p=0.25):
        self.GOOGLE_API_KEY = GOOGLE_API_KEY
        self.job_text = job_text
        self.resume_text = resume_text
        self.model = model
        self.temperature= temperature
        self.top_p = top_p
        self.top_k = top_k
        self.timeout = 120
        self.tech_skills = []
        self.prompts = {
            'tech_skills_extraction': '''Extract a comma-separated list of technical skills and tools required for this position,
                                            Such as programming languages, frameworks, software, platforms, etc.
                                            Only list the keywords, no explanations. Do not include soft skills, salary, or benefits.
    
                                            Job Description:{} Technical Skills and Tools:"
                                    '''.format(self.job_text),
            'soft_skills_extraction': '''Extract a comma-separated list of soft skills required for this position,
                                            Such as communication, teamwork, problem-solving, leadership, etc.
                                            Only list the keywords, no explanations. Do not include technical skills, salary, or benefits.
                                            Job Description:{} Soft Skills:"
                                    '''.format(self.job_text),
            'salary_extraction': '''Based on the following job description, extract the estimated salary or salary range.
                                        Do not include any other information, just the salary or range.
                                        If no salary is mentioned, reply with 'Salary Not specified'.
                                        Job Description:{} Salary:
                                        '''.format(self.job_text),
            
            'check_skills_in_resume':  '''Given the following list of technical skills and the resume text,
                                                return a JSON array of objects, each with 'keyword' and 'in_resume' (true/false),
                                                indicating if the skill is present in the resume.
                                                Only use the keywords provided, and do not add explanations.
                                                Make sure the skills are organize by in_resume true first.
                                                Keywords: {}
                                                Resume:{}
                                                Output:
                                        ''',
            'convert_resume' : ''' You are an expert Human Resources agent working for a client that is looking for a job.
                                    This job descripion is a good opportunity {} for your client.
                                    Convert your clients resume {} to match the above job description, make sure to highlight your clients expertise.
                                    Your response should ba a python dictionary where the keys correspond to the resume sections: 'Summary', 'Experience', 'Skills', 'Education', 'Leadership'.
                                    and the values are the content for each section, 
                                    The 'Summary' (an string) section should be a brief overview of the candidate's qualifications, experience, and career goals. 
                                    Make sure the 'Summary' aligns with the job description and highlights relevant clinet experience and skills.
                                    The 'Experience' section should be a list of dictionaries, each dictionary representing a job with keys for 'Title', 'Company', 'Location', 'Duration', and 'Highlights'.
                                    All experiences must have 3 highlights and each must be a relevant achievement and quantifiable result that align with the job description. 
                                    The 'Skills' section should be a list of dictionaries with relevant skills extracted from the resume, and split into 'Technical' and 'Soft Skills'
                                    Each skill should be placed on its own dictionary with a key for 'Skill' and 'Proficiency Level' if available.
                                    The proficiency level can be Beginner, Intermediate, Advanced, Expert.
                                    If proficiency not available just leave it blank.
                                    Use all the skills in the resume, but sort them so that the most relevant skills to the job description are at the top of each list.
                                    The Education should be a list of dictionaries with keys for 'Degree', 'Institution'
                                    The 'Leadership' section should be an statement with highlights of leadership shown in the resume'.
                                    Do not include any information that is not relevant to the job description.
                                    Make sure to format the content in a way that is clear and easy to read.
                                    Provide the output as a JSON array of objects. Exclude any comments or explanations.
                                    In the output dictionary, add quotes before and after all squared parentheses to make it valid JSON.
                                    In all fields highlight the parts that match between job description and the resume.
                                '''.format(self.job_text, self.resume_text
                                )
        }
    
    def run_genai(self, prompt):
        client = Client(api_key=self.GOOGLE_API_KEY)
        try: 
            response = client.models.generate_content(
                    model=self.model,
                    contents = prompt,
                    config=types.GenerateContentConfig(
                                                        temperature= self.temperature,
                            top_p=self.top_p,
                            top_k=self.top_k,
                                                        )
                    )
        except errors.APIError as e:
            response = "API Error: {}".format(e.message)
        client.close()
        return response
    
    def run_client(self, prompt):
        result = self.run_genai(prompt + ''' Do not include any explanations, just the answer. Additionaly, DO NOT include any character (e.g. *, **) highlighting a feature, 
                                            work, keyworks, skill, or comparison
                                ''')
        result_status = True if "API Error" not in result else False
        return result, result_status
    
    def extract_tech_skills(self):
        result, result_status = self.run_client(self.prompts['tech_skills_extraction'])
        if result_status:
            # Split by commas and clean up whitespace
            self.tech_skills = [kw.strip() for kw in result.text.split(",") if kw.strip()]
        else:
            self.tech_skills = []

    def extract_soft_skills(self):
        result, result_status = self.run_client(self.prompts['soft_skills_extraction'])
        if result_status:
            # Split by commas and clean up whitespace
            self.soft_skills = [kw.strip() for kw in result.text.split(",") if kw.strip()]
        else:
            self.soft_skills = []

    def extract_salary(self):
        result, result_status = self.run_client(self.prompts['salary_extraction'])
        if result_status:
            self.salary =  result.text.strip()
        else:
            self.salary =  "Not specified"

    def compare_skills(self, type = ['soft','tech']):
        if self.tech_skills == []:
            return []
        if type == 'tech':
            keywords = self.tech_skills
        else:
            keywords = self.soft_skills
        keywords = ", ".join(keywords)
        prompt = self.prompts['check_skills_in_resume'].format(keywords, self.resume_text)
        result, result_status = self.run_client(prompt)
        if result_status:
            result = result.text.strip()
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
    
    def convert_resume(self):
        result, result_status = self.run_client(self.prompts['convert_resume'])
        result = result.text
        if result_status:
            try:
                # Clean the response by finding the dictionary boundaries
                result = result.strip()
                start = result.find('{')
                end = result.rfind('}')
                if start != -1 and end != -1:
                    clean_result = result[start:end+1]
                    self.new_resume = json.loads(clean_result.strip().replace('\n', ""))
                else:
                    raise ValueError("No valid dictionary found in response")
            except (json.JSONDecodeError, ValueError) as e:
                print("Error parsing JSON:{}".format(e))
                self.new_resume = "Error parsing response"
        else:
            self.new_resume = "Not specified"

    def run_process(self):
        print("Extracting technical skills...")
        self.extract_tech_skills()
        print("Extracting soft skills...")
        self.extract_soft_skills()
        print("Extracting salary...")
        self.extract_salary()
        print("Comparing technical skills...")
        self.comparison = self.compare_skills('tech')
        print("Comparing soft skills...")
        self.soft_comparison = self.compare_skills('soft')
        print("Converting resume...")
        self.convert_resume()
        print('DONE PROCESSING')
        return self.comparison, self.soft_comparison, self.salary, self.new_resume
    
    
