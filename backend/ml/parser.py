import pdfplumber
import docx
import re
from typing import Dict, List, Optional
import spacy
from datetime import datetime

class IndianResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ spaCy model not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Enhanced section patterns with ML-like scoring
        self.section_patterns = {
            'education': {
                'keywords': ['education', 'qualification', 'academic', 'degree', 'b.tech', 'm.tech', 'b.e', 'mca', 'b.sc', 'm.sc', 'cgpa', 'percentage', 'university', 'college', 'school', '12th', '10th', 'ssc', 'hsc', 'EDUCATION'],
                'exclude': ['experience', 'project', 'skill'],
                'min_lines': 2,
                'weight': 1.0
            },
            'experience': {
                'keywords': ['experience', 'work', 'employment', 'job', 'professional', 'career', 'worked', 'company', 'employer', 'responsibilities', 'achievements', 'EXPERIENCE', 'WORK EXPERIENCE'],
                'exclude': ['education', 'project', 'skill'],
                'min_lines': 2,
                'weight': 1.0
            },
            'skills': {
                'keywords': ['skills', 'technical skills', 'competencies', 'technologies', 'tools', 'programming', 'languages', 'frameworks', 'expertise', 'SKILLS', 'TECHNICAL SKILLS'],
                'exclude': ['experience', 'education'],
                'min_lines': 1,
                'weight': 1.0
            },
            'projects': {
                'keywords': ['projects', 'academic projects', 'personal projects', 'github', 'portfolio', 'developed', 'built', 'created', 'PROJECTS'],
                'exclude': ['experience', 'skills'],
                'min_lines': 2,
                'weight': 0.8
            },
            'certifications': {
                'keywords': ['certifications', 'certified', 'certificate', 'courses', 'training', 'credentials', 'aws certified', 'google certified', 'microsoft certified', 'CERTIFICATIONS'],
                'exclude': ['education', 'skills'],
                'min_lines': 1,
                'weight': 0.7
            },
            'achievements': {
                'keywords': ['achievements', 'awards', 'honors', 'recognition', 'scholarship', 'prize', 'winner', 'ACHIEVEMENTS'],
                'exclude': ['experience', 'skills'],
                'min_lines': 1,
                'weight': 0.6
            },
            'summary': {
                'keywords': ['summary', 'profile', 'objective', 'about me', 'professional summary', 'career objective', 'SUMMARY', 'PROFESSIONAL SUMMARY'],
                'exclude': ['experience', 'skills'],
                'min_lines': 1,
                'weight': 0.5
            },
            'languages': {
                'keywords': ['languages', 'language proficiency', 'spoken languages', 'english', 'hindi', 'regional', 'LANGUAGES'],
                'exclude': ['skills'],
                'min_lines': 1,
                'weight': 0.4
            },
            'publications': {
                'keywords': ['publications', 'papers', 'research', 'articles', 'blogs', 'PUBLICATIONS'],
                'exclude': ['experience', 'skills'],
                'min_lines': 1,
                'weight': 0.4
            }
        }
        
        # Indian degree patterns (enhanced)
        self.indian_degree_patterns = [
            r'B\.?Tech', r'B\.?E\.?', r'M\.?Tech', r'B\.?Sc', 
            r'M\.?Sc', r'BCA', r'MCA', r'B\.?Com', r'M\.?Com',
            r'Class X', r'Class XII', r'10th', r'12th', r'SSC', r'HSC',
            r'BBA', r'MBA', r'PGDM', r'B\.?Arch', r'M\.?Arch',
            r'B\.?Pharm', r'M\.?Pharm', r'BDS', r'MBBS', r'MD',
            r'B\.?Ed', r'M\.?Ed', r'LLB', r'LLM', r'BA', r'MA',
            r'Diploma', r'PG Diploma', r'PhD', r'Doctorate'
        ]
        
        # Indian company patterns (enhanced with mapping)
        self.indian_company_patterns = {
            'tcs': r'TCS|Tata Consultancy Services|Tata Consultancy',
            'infosys': r'Infosys|Infy',
            'wipro': r'Wipro|Wipro Technologies',
            'hcl': r'HCL|HCL Technologies',
            'tech_mahindra': r'Tech Mahindra|TechMahindra',
            'accenture': r'Accenture',
            'cognizant': r'Cognizant|CTS',
            'capgemini': r'Capgemini',
            'ibm': r'IBM|International Business Machines',
            'microsoft': r'Microsoft',
            'amazon': r'Amazon|AWS',
            'google': r'Google',
            'flipkart': r'Flipkart',
            'paytm': r'Paytm|One97',
            'ola': r'Ola|Ola Cabs',
            'uber': r'Uber',
            'swiggy': r'Swiggy',
            'zomato': r'Zomato',
            'oyo': r'OYO|OYO Rooms',
            'phonepe': r'PhonePe',
            'icici': r'ICICI|ICICI Bank',
            'hdfc': r'HDFC|HDFC Bank',
            'sbi': r'SBI|State Bank of India',
            'axis': r'Axis|Axis Bank',
            'kotak': r'Kotak|Kotak Mahindra Bank',
            'yes_bank': r'Yes Bank'
        }
        
        # Indian cities with variations
        self.indian_cities = {
            'mumbai': ['Mumbai', 'Bombay', 'Mumbai Suburban'],
            'delhi': ['Delhi', 'New Delhi', 'NCR', 'Delhi NCR', 'Gurugram', 'Gurgaon', 'Noida'],
            'bangalore': ['Bangalore', 'Bengaluru', 'BLR'],
            'chennai': ['Chennai', 'Madras'],
            'hyderabad': ['Hyderabad', 'Secunderabad'],
            'pune': ['Pune', 'Poona'],
            'kolkata': ['Kolkata', 'Calcutta'],
            'ahmedabad': ['Ahmedabad', 'Amdavad'],
            'jaipur': ['Jaipur'],
            'lucknow': ['Lucknow'],
            'indore': ['Indore'],
            'nagpur': ['Nagpur'],
            'chandigarh': ['Chandigarh'],
            'bhopal': ['Bhopal'],
            'visakhapatnam': ['Visakhapatnam', 'Vizag'],
            'patna': ['Patna'],
            'vadodara': ['Vadodara', 'Baroda'],
            'surat': ['Surat']
        }
        
        # Company Normalizations
        self.company_normalizations = {
            "tcs": "Tata Consultancy Services (TCS)",
            "infosys": "Infosys Ltd",
            "infy": "Infosys Ltd",
            "wipro": "Wipro Technologies",
            "hcl": "HCL Technologies",
            "tech mahindra": "Tech Mahindra",
            "techm": "Tech Mahindra",
            "cognizant": "Cognizant (CTS)",
            "cts": "Cognizant (CTS)",
            "accenture": "Accenture India",
            "capgemini": "Capgemini India",
            "ibm": "IBM India",
            "microsoft": "Microsoft India",
            "amazon": "Amazon India",
            "google": "Google India",
            "icici": "ICICI Bank",
            "hdfc": "HDFC Bank",
            "sbi": "State Bank of India",
            "axis": "Axis Bank",
            "kotak": "Kotak Mahindra Bank",
            "yes bank": "Yes Bank",
            "flipkart": "Flipkart India",
            "ola": "Ola Cabs",
            "uber": "Uber India",
            "paytm": "Paytm",
            "phonepe": "PhonePe",
            "swiggy": "Swiggy",
            "zomato": "Zomato",
            "oyo": "OYO Rooms"
        }
        
        # Degree Normalizations
        self.degree_normalizations = {
            "b.tech": "Bachelor of Technology (B.Tech)",
            "btech": "Bachelor of Technology (B.Tech)",
            "b.e": "Bachelor of Engineering (B.E.)",
            "be": "Bachelor of Engineering (B.E.)",
            "m.tech": "Master of Technology (M.Tech)",
            "mtech": "Master of Technology (M.Tech)",
            "m.e": "Master of Engineering (M.E.)",
            "me": "Master of Engineering (M.E.)",
            "bca": "Bachelor of Computer Applications (BCA)",
            "mca": "Master of Computer Applications (MCA)",
            "b.sc": "Bachelor of Science (B.Sc)",
            "bsc": "Bachelor of Science (B.Sc)",
            "m.sc": "Master of Science (M.Sc)",
            "msc": "Master of Science (M.Sc)",
            "b.com": "Bachelor of Commerce (B.Com)",
            "bcom": "Bachelor of Commerce (B.Com)",
            "m.com": "Master of Commerce (M.Com)",
            "mcom": "Master of Commerce (M.Com)",
            "bba": "Bachelor of Business Administration (BBA)",
            "mba": "Master of Business Administration (MBA)",
            "pgdm": "Post Graduate Diploma in Management",
            "ba": "Bachelor of Arts (B.A.)",
            "ma": "Master of Arts (M.A.)",
            "b.arch": "Bachelor of Architecture (B.Arch)",
            "m.arch": "Master of Architecture (M.Arch)",
            "b.pharm": "Bachelor of Pharmacy (B.Pharm)",
            "m.pharm": "Master of Pharmacy (M.Pharm)",
            "mbbs": "Bachelor of Medicine, Bachelor of Surgery (MBBS)",
            "bds": "Bachelor of Dental Surgery (BDS)",
            "md": "Doctor of Medicine (MD)",
            "llb": "Bachelor of Laws (LLB)",
            "llm": "Master of Laws (LLM)",
            "b.ed": "Bachelor of Education (B.Ed)",
            "m.ed": "Master of Education (M.Ed)",
            "10th": "Secondary School Certificate (SSC)",
            "ssc": "Secondary School Certificate (SSC)",
            "12th": "Higher Secondary Certificate (HSC)",
            "hsc": "Higher Secondary Certificate (HSC)",
            "cbse": "CBSE Board",
            "icse": "ICSE Board",
            "state board": "State Board of Education",
            "diploma": "Diploma",
            "pg diploma": "Post Graduate Diploma",
            "phd": "Doctor of Philosophy (PhD)",
            "doctorate": "Doctorate"
        }
        
        # Location Normalizations
        self.location_normalizations = {
            "bengaluru": "Bengaluru/Bangalore",
            "bangalore": "Bengaluru/Bangalore",
            "bombay": "Mumbai",
            "mumbai": "Mumbai",
            "delhi": "Delhi NCR",
            "new delhi": "Delhi NCR",
            "ncr": "Delhi NCR",
            "gurugram": "Gurugram/Gurgaon",
            "gurgaon": "Gurugram/Gurgaon",
            "noida": "Noida",
            "chennai": "Chennai",
            "madras": "Chennai",
            "hyderabad": "Hyderabad",
            "secunderabad": "Hyderabad",
            "pune": "Pune",
            "poonamallee": "Pune",
            "kolkata": "Kolkata",
            "calcutta": "Kolkata",
            "ahmedabad": "Ahmedabad",
            "jaipur": "Jaipur",
            "lucknow": "Lucknow",
            "indore": "Indore",
            "nagpur": "Nagpur",
            "chandigarh": "Chandigarh",
            "bhopal": "Bhopal",
            "visakhapatnam": "Visakhapatnam/Vizag",
            "vizag": "Visakhapatnam/Vizag",
            "patna": "Patna",
            "vadodara": "Vadodara/Baroda",
            "baroda": "Vadodara/Baroda",
            "surat": "Surat"
        }
        
        # Skill Synonyms
        self.skill_synonyms = {
            "python": ["Python", "Python3", "Django", "Flask", "FastAPI"],
            "java": ["Java", "J2EE", "Spring", "Spring Boot", "Hibernate"],
            "javascript": ["JavaScript", "JS", "ES6", "Node.js", "React.js", "Angular", "Vue.js"],
            "react": ["React", "React.js", "ReactJS", "Next.js"],
            "angular": ["Angular", "AngularJS", "Angular 2+"],
            "database": ["SQL", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "NoSQL"],
            "cloud": ["AWS", "Azure", "GCP", "Cloud Computing"],
            "devops": ["Docker", "Kubernetes", "Jenkins", "Git", "CI/CD", "Terraform"],
            "ai_ml": ["Machine Learning", "Deep Learning", "AI", "TensorFlow", "PyTorch", "Scikit-learn"],
            "data_science": ["Data Science", "Data Analysis", "Pandas", "NumPy", "Matplotlib"],
            "mobile": ["Android", "iOS", "Kotlin", "Swift", "Flutter", "React Native"],
            "frontend": ["HTML", "CSS", "Bootstrap", "Tailwind", "jQuery"],
            "backend": ["Node.js", "Django", "Flask", "Spring Boot", "Express.js"],
            "testing": ["JUnit", "Selenium", "PyTest", "Jest", "Mocha"]
        }
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from PDF or DOCX with better error handling"""
        text = ""
        
        try:
            if file_type == 'pdf':
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                            
            elif file_type == 'docx':
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
                    
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
        
        return text.strip()
    
    def parse_resume(self, text: str) -> Dict:
        """Enhanced resume parsing with improved section detection"""
        if not text:
            return self._get_empty_response()
        
        try:
            lines = text.split('\n')
            
            # Detect sections using improved method
            sections = self._detect_sections_improved(lines)
            
            # Extract entities
            entities = self._extract_entities(text)
            
            # Extract Indian-specific info
            indian_info = self._extract_indian_info(text)
            
            # Extract enhanced data
            skills = self._extract_skills_enhanced(text)
            experience = self._extract_experience_improved(text)
            education = self._extract_education_improved(text)
            
            # Expand skills with synonyms
            expanded_skills = self.expand_skills(skills)
            
            return {
                "raw_text": text,
                "sections": sections,
                "entities": entities,
                "indian_specific": indian_info,
                "skills": expanded_skills,
                "original_skills": skills,
                "experience": experience,
                "education": education,
                "stats": {
                    "total_lines": len(lines),
                    "sections_found": len(sections),
                    "skills_count": len(skills),
                    "experience_count": len(experience)
                }
            }
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return self._get_empty_response()
    
    def _get_empty_response(self) -> Dict:
        """Return empty response structure"""
        return {
            "raw_text": "",
            "sections": {},
            "entities": {
                "PERSON": [], "ORG": [], "GPE": [], "DATE": [], "EMAIL": [], "PHONE": []
            },
            "indian_specific": {
                "degrees": [], "companies": [], "locations": [],
                "normalized": {"degrees": [], "companies": [], "locations": []}
            },
            "skills": [],
            "original_skills": [],
            "experience": [],
            "education": [],
            "stats": {
                "total_lines": 0,
                "sections_found": 0,
                "skills_count": 0,
                "experience_count": 0
            }
        }
    
    def _detect_sections_improved(self, lines: List[str]) -> Dict[str, str]:
        """Improved section detection with hardcoded patterns"""
        sections = {}
        current_section = "HEADER"
        current_content = []
        
        # Common section headers in ALL CAPS
        section_headers = {
            'summary': ['SUMMARY', 'PROFESSIONAL SUMMARY', 'CAREER SUMMARY', 'PROFILE'],
            'skills': ['SKILLS', 'TECHNICAL SKILLS', 'CORE COMPETENCIES', 'TECHNOLOGIES'],
            'experience': ['EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE'],
            'education': ['EDUCATION', 'ACADEMIC BACKGROUND', 'QUALIFICATIONS'],
            'projects': ['PROJECTS', 'KEY PROJECTS', 'PERSONAL PROJECTS'],
            'certifications': ['CERTIFICATIONS', 'CERTIFICATES', 'LICENSES'],
            'achievements': ['ACHIEVEMENTS', 'AWARDS', 'HONORS'],
            'publications': ['PUBLICATIONS', 'PAPERS', 'RESEARCH'],
            'languages': ['LANGUAGES', 'LANGUAGE PROFICIENCY']
        }
        
        try:
            for line in lines:
                line_strip = line.strip()
                if not line_strip:
                    continue
                    
                line_upper = line_strip.upper()
                
                # Check if this line is a section header
                found_section = False
                for section, headers in section_headers.items():
                    if any(header in line_upper for header in headers):
                        # Save previous section
                        if current_section != "HEADER" and current_content:
                            sections[current_section.lower()] = '\n'.join(current_content)
                        current_section = section
                        current_content = []
                        found_section = True
                        break
                
                if not found_section:
                    current_content.append(line_strip)
            
            # Add last section
            if current_content and current_section:
                sections[current_section.lower()] = '\n'.join(current_content)
                
        except Exception as e:
            print(f"Error in section detection: {e}")
            
        return sections
    
    def _extract_skills_enhanced(self, text: str) -> List[str]:
        """Enhanced skill extraction with context awareness"""
        if not text:
            return []
        
        try:
            # Extended skill database with categories
            skill_database = {
                'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript', 'php', 'scala', 'r'],
                'web_frameworks': ['django', 'flask', 'fastapi', 'spring', 'spring boot', 'react', 'angular', 'vue', 'node.js', 'express', 'asp.net', 'rails'],
                'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'cassandra', 'elasticsearch', 'dynamodb', 'mariadb'],
                'cloud': ['aws', 'azure', 'gcp', 'cloud', 'lambda', 'ec2', 's3', 'cloudformation', 'terraform'],
                'devops': ['docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'ansible', 'prometheus', 'grafana', 'elk'],
                'data_science': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'tableau', 'power bi'],
                'mobile': ['android', 'ios', 'flutter', 'react native', 'xamarin', 'kotlin', 'swift'],
                'tools': ['git', 'github', 'gitlab', 'jira', 'confluence', 'postman', 'vscode', 'intellij', 'eclipse'],
                'testing': ['junit', 'selenium', 'pytest', 'jest', 'mocha', 'cypress', 'testng'],
                'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'analytical', 'critical thinking', 'time management']
            }
            
            found_skills = set()
            text_lower = text.lower()
            
            # Check each category
            for category, skills in skill_database.items():
                for skill in skills:
                    # Exact match
                    if skill in text_lower:
                        found_skills.add(skill)
                    # Word boundary match for longer skills
                    elif len(skill) > 4 and re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                        found_skills.add(skill)
            
            # Also check for skills in the original list for backward compatibility
            indian_tech_skills = [
                'Java', 'Python', 'JavaScript', 'React', 'Angular', 'Node.js',
                'Spring Boot', 'Django', 'Flask', 'MySQL', 'MongoDB', 'Oracle',
                'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Jenkins',
                'Machine Learning', 'Data Science', 'Android', 'iOS',
                'HTML', 'CSS', 'Bootstrap', 'jQuery', 'REST API', 'Microservices'
            ]
            
            for skill in indian_tech_skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill)
            
            return sorted(list(found_skills))
            
        except Exception as e:
            print(f"Error in skill extraction: {e}")
            return []
    
    def _extract_experience_improved(self, text: str) -> List[Dict]:
        """Improved experience extraction with proper job parsing"""
        experience = []
        
        if not text:
            return experience
            
        try:
            lines = text.split('\n')
            in_experience = False
            current_job = {}
            current_desc = []
            
            # List of known companies to identify job lines
            known_companies = ['AMAZON', 'FLIPKART', 'TCS', 'INFOSYS', 'WIPRO', 'MICROSOFT', 'GOOGLE', 'IBM', 'ACCENTURE', 'COGNIZANT']
            
            for line in lines:
                line_strip = line.strip()
                if not line_strip:
                    continue
                
                line_upper = line_strip.upper()
                
                # Check if this is a job header (contains company name and possibly role)
                is_job_header = False
                for company in known_companies:
                    if company in line_upper:
                        is_job_header = True
                        break
                
                # Also check for patterns like "Company - Role" or "Company | Role"
                if '|' in line_strip or ' - ' in line_strip or '–' in line_strip:
                    parts = re.split(r'[|\-–]', line_strip)
                    if len(parts) >= 2 and any(company in parts[0].upper() for company in known_companies):
                        is_job_header = True
                
                if is_job_header:
                    # Save previous job
                    if current_job and current_desc:
                        current_job['description'] = '\n'.join(current_desc)
                        experience.append(current_job)
                    
                    # Parse new job
                    parts = re.split(r'[|\-–]', line_strip)
                    current_job = {
                        'company': parts[0].strip(),
                        'role': parts[1].strip() if len(parts) > 1 else '',
                        'duration': '',
                        'description': ''
                    }
                    current_desc = []
                    in_experience = True
                
                # Check for duration (years pattern)
                elif in_experience and re.search(r'20\d{2}\s*[-–]\s*(Present|20\d{2}|Current)', line_strip):
                    current_job['duration'] = line_strip
                
                # Add bullet points or description lines
                elif in_experience and (line_strip.startswith(('•', '-', '*')) or line_strip[0].isdigit() and line_strip[1] == '.'):
                    current_desc.append(line_strip)
                
                # Add non-empty lines that might be description
                elif in_experience and len(line_strip) > 10 and not any(section in line_upper for section in ['EDUCATION', 'SKILLS', 'PROJECTS']):
                    current_desc.append(line_strip)
            
            # Add last job
            if current_job and current_desc:
                current_job['description'] = '\n'.join(current_desc)
                experience.append(current_job)
                
        except Exception as e:
            print(f"Error in experience extraction: {e}")
            
        return experience
    
    def _extract_education_improved(self, text: str) -> List[Dict]:
        """Improved education extraction"""
        education = []
        
        if not text:
            return education
            
        try:
            lines = text.split('\n')
            in_education = False
            edu_text = []
            
            for line in lines:
                line_upper = line.upper()
                
                if 'EDUCATION' in line_upper:
                    in_education = True
                    continue
                
                if in_education:
                    # Stop at next major section
                    if any(section in line_upper for section in ['EXPERIENCE', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS']):
                        break
                    if line.strip():
                        edu_text.append(line.strip())
            
            if edu_text:
                edu_entry = {}
                edu_full = ' '.join(edu_text)
                
                # Extract degree
                degree_patterns = [
                    r'(B\.?Tech|B\.?E\.?|M\.?Tech|MCA|BCA|B\.?Sc|M\.?Sc|B\.?Com|M\.?Com|MBA|BBA|Diploma|PhD)',
                    r'(Bachelor|Master|Doctorate)\s+of\s+(\w+)',
                    r'(10th|12th|SSC|HSC|CBSE|ICSE)'
                ]
                for pattern in degree_patterns:
                    match = re.search(pattern, edu_full, re.IGNORECASE)
                    if match:
                        edu_entry['degree'] = match.group()
                        break
                
                # Extract institution
                institution_patterns = [
                    r'(IIT|NIT|IIIT|BITS|VIT|SRM|LPU)\s+\w+',
                    r'(University|College|Institute)\s+of\s+\w+',
                    r'\w+\s+(University|College|Institute)'
                ]
                for pattern in institution_patterns:
                    match = re.search(pattern, edu_full, re.IGNORECASE)
                    if match:
                        edu_entry['institution'] = match.group()
                        break
                
                # Extract year
                year_match = re.search(r'(19|20)\d{2}', edu_full)
                if year_match:
                    edu_entry['year'] = year_match.group()
                
                # Extract CGPA
                cgpa_match = re.search(r'CGPA[:\s]*(\d+\.?\d*)', edu_full, re.IGNORECASE)
                if cgpa_match:
                    edu_entry['cgpa'] = cgpa_match.group(1)
                else:
                    percent_match = re.search(r'(\d{2,3})%', edu_full)
                    if percent_match:
                        edu_entry['percentage'] = percent_match.group(1)
                
                education.append(edu_entry)
                
        except Exception as e:
            print(f"Error in education extraction: {e}")
            
        return education
    
    def expand_skills(self, skills_list: List[str]) -> List[str]:
        """Add related skills based on synonyms"""
        if not skills_list:
            return []
            
        try:
            expanded = set(skills_list)
            
            for skill in skills_list:
                if not skill:
                    continue
                skill_lower = skill.lower()
                for category, synonyms in self.skill_synonyms.items():
                    if skill_lower in category or any(s.lower() in skill_lower for s in synonyms):
                        expanded.update(synonyms[:4])
            
            return list(set(expanded))
        except Exception as e:
            print(f"Error expanding skills: {e}")
            return skills_list
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy"""
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Locations
            "DATE": [],
            "EMAIL": [],
            "PHONE": []
        }
        
        if not text:
            return entities
            
        try:
            doc = self.nlp(text[:10000])  # Limit text for performance
            
            # Extract entities from spaCy
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
            
            # Extract email and phone (regex patterns)
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b(?:\+91[\-\s]?)?[6789]\d{9}\b'  # Indian phone numbers
            
            entities["EMAIL"] = re.findall(email_pattern, text)
            entities["PHONE"] = re.findall(phone_pattern, text)
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
                
        except Exception as e:
            print(f"Error extracting entities: {e}")
            
        return entities
    
    # ===== NORMALIZATION METHODS =====
    
    def normalize_company(self, company_name: Optional[str]) -> str:
        """Convert short/nicknames to proper company names"""
        if not company_name:
            return ""
        
        try:
            company_lower = str(company_name).lower().strip()
            
            # Check for exact matches
            for key, normalized in self.company_normalizations.items():
                if key in company_lower:
                    return normalized
            
            return company_name
        except Exception as e:
            print(f"Error normalizing company: {e}")
            return company_name or ""
    
    def normalize_degree(self, degree_text: Optional[str]) -> str:
        """Convert degree abbreviations to full forms"""
        if not degree_text:
            return ""
        
        try:
            degree_lower = str(degree_text).lower().strip()
            degree_lower = degree_lower.replace('.', '')
            
            for key, normalized in self.degree_normalizations.items():
                if key in degree_lower:
                    return normalized
            
            return degree_text
        except Exception as e:
            print(f"Error normalizing degree: {e}")
            return degree_text or ""
    
    def normalize_location(self, location: Optional[str]) -> str:
        """Standardize Indian city names"""
        if not location:
            return ""
        
        try:
            location_lower = str(location).lower().strip()
            
            for key, normalized in self.location_normalizations.items():
                if key in location_lower:
                    return normalized
            
            return location
        except Exception as e:
            print(f"Error normalizing location: {e}")
            return location or ""
    
    def _extract_indian_info(self, text: str) -> Dict:
        """Extract Indian-specific information with normalization"""
        info = {
            "degrees": [],
            "companies": [],
            "locations": [],
            "normalized": {
                "degrees": [],
                "companies": [],
                "locations": []
            }
        }
        
        if not text:
            return info
            
        try:
            # Extract and normalize Indian degrees
            for pattern in self.indian_degree_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if match:
                        info["degrees"].append(match)
                        info["normalized"]["degrees"].append(self.normalize_degree(match))
            
            # Extract and normalize Indian companies
            for company_key, pattern in self.indian_company_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if match:
                        info["companies"].append(match)
                        info["normalized"]["companies"].append(self.normalize_company(match))
            
            # Extract and normalize Indian locations
            for city, variations in self.indian_cities.items():
                for var in variations:
                    if var.lower() in text.lower():
                        info["locations"].append(city.title())
                        info["normalized"]["locations"].append(self.normalize_location(city))
                        break
            
            # Remove duplicates
            for key in info:
                if isinstance(info[key], list):
                    info[key] = list(dict.fromkeys(info[key]))
            
            for key in info["normalized"]:
                info["normalized"][key] = list(dict.fromkeys(info["normalized"][key]))
                
        except Exception as e:
            print(f"Error extracting Indian info: {e}")
            
        return info