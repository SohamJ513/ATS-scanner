# ============================================
# SEMANTIC_MATCHER.PY - Sentence Transformers for semantic similarity
# ============================================

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import re

class SemanticMatcher:
    def __init__(self):
        """Initialize the sentence transformer model"""
        print("🔄 Loading semantic matching model...")
        # Using all-MiniLM-L6-v2 - lightweight (80MB) and fast
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Semantic model loaded successfully!")
        
        # Download NLTK stopwords if not already present
        try:
            self.stopwords = set(stopwords.words('english'))
        except:
            nltk.download('stopwords')
            self.stopwords = set(stopwords.words('english'))
        
        # ENHANCED: Expanded skill synonyms for better matching
        self.skill_synonyms = {
            # Cloud & DevOps
            "aws": ["AWS", "Amazon Web Services", "EC2", "S3", "Lambda", "CloudFormation", "ECS", "EKS", "Amplify"],
            "azure": ["Azure", "Microsoft Azure", "Azure DevOps", "App Services", "Functions", "Azure Cloud", "MS Azure"],
            "gcp": ["GCP", "Google Cloud", "Google Cloud Platform", "Compute Engine", "Cloud Run", "Google Kubernetes Engine"],
            "docker": ["Docker", "Container", "Containerization", "Dockerfile", "Docker Compose", "Containers"],
            "kubernetes": ["Kubernetes", "K8s", "EKS", "AKS", "GKE", "Container Orchestration", "Kube"],
            "terraform": ["Terraform", "Infrastructure as Code", "IaC"],
            "jenkins": ["Jenkins", "CI/CD", "Jenkins Pipeline", "Continuous Integration", "Jenkinsfile"],
            
            # Languages
            "python": ["Python", "Python3", "Django", "Flask", "FastAPI", "NumPy", "Pandas", "Jupyter", "Python Programming"],
            "java": ["Java", "J2EE", "Spring", "Spring Boot", "Hibernate", "Maven", "Gradle", "Java 8", "Java 11"],
            "javascript": ["JavaScript", "JS", "ES6", "Node.js", "Express.js", "React.js", "Angular", "Vue.js", "Vanilla JS"],
            "typescript": ["TypeScript", "TS", "Angular", "NestJS", "Type Script"],
            "c++": ["C++", "CPP", "C plus plus", "C with Classes"],
            "c#": ["C#", "C Sharp", ".NET", "Dotnet", "ASP.NET", "C Sharp Programming"],
            "go": ["Go", "Golang", "Go Lang"],
            "rust": ["Rust", "Rust Lang", "Rust Programming"],
            "php": ["PHP", "Laravel", "Symfony", "CodeIgniter", "PHP Hypertext Preprocessor"],
            "ruby": ["Ruby", "Ruby on Rails", "Rails"],
            
            # Web Frameworks
            "react": ["React", "React.js", "ReactJS", "Next.js", "Redux", "React Native", "React Hooks"],
            "angular": ["Angular", "AngularJS", "Angular 2+", "Angular 4", "Angular 5", "Angular 6", "Angular 7", "Angular 8", "Angular 9", "Angular 10", "Angular 11", "Angular 12", "Angular 13", "Angular 14", "Angular 15", "Angular 16"],
            "vue": ["Vue", "Vue.js", "VueJS", "Nuxt.js", "Vuex"],
            "django": ["Django", "Django REST Framework", "DRF", "Django ORM"],
            "flask": ["Flask", "Flask RESTful", "Flask API"],
            "fastapi": ["FastAPI", "Fast API", "Python API"],
            "spring": ["Spring", "Spring Boot", "Spring MVC", "Spring Framework", "Spring Cloud", "Spring Data"],
            "node": ["Node", "Node.js", "NodeJS", "Express.js", "NestJS"],
            "express": ["Express", "Express.js", "ExpressJS"],
            "nextjs": ["Next.js", "NextJS", "Next"],
            
            # Databases
            "sql": ["SQL", "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server", "T-SQL", "PL/SQL", "Structured Query Language"],
            "nosql": ["NoSQL", "MongoDB", "Cassandra", "DynamoDB", "Firebase", "CouchDB", "Couchbase"],
            "mongodb": ["MongoDB", "Mongo", "NoSQL", "Mongoose", "Mongo DB"],
            "postgresql": ["PostgreSQL", "Postgres", "PSQL", "Postgres SQL"],
            "mysql": ["MySQL", "My SQL", "MariaDB"],
            "oracle": ["Oracle", "Oracle DB", "Oracle Database", "Oracle SQL"],
            "redis": ["Redis", "Redis Cache", "Remote Dictionary Server"],
            "elasticsearch": ["Elasticsearch", "ELK", "Elastic Stack", "ES"],
            
            # Data Science & ML
            "machine learning": ["Machine Learning", "ML", "Deep Learning", "AI", "Artificial Intelligence", "ML Models"],
            "deep learning": ["Deep Learning", "Neural Networks", "CNN", "RNN", "LSTM", "GRU", "Transformers"],
            "tensorflow": ["TensorFlow", "TF", "Keras", "Tensor Flow", "TF 2.0"],
            "pytorch": ["PyTorch", "Torch", "Py Torch"],
            "pandas": ["Pandas", "Data Analysis", "Data Manipulation", "Python Data Analysis"],
            "numpy": ["NumPy", "Numerical Python", "Numeric Python"],
            "scikit-learn": ["Scikit-learn", "sklearn", "Machine Learning Python"],
            "data science": ["Data Science", "Data Analytics", "Data Analysis", "Data Scientist"],
            "data visualization": ["Data Visualization", "Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly"],
            "tableau": ["Tableau", "Tableau Desktop", "Tableau Server"],
            "power bi": ["Power BI", "PowerBI", "Microsoft Power BI"],
            
            # Testing
            "testing": ["Testing", "JUnit", "Selenium", "PyTest", "Jest", "Mocha", "Cypress", "TestNG", "Unit Testing"],
            "junit": ["JUnit", "JUnit 4", "JUnit 5", "Unit Testing Java"],
            "selenium": ["Selenium", "Selenium WebDriver", "Web Testing", "Automation Testing"],
            "pytest": ["PyTest", "Python Testing", "Pytest"],
            "jest": ["Jest", "JavaScript Testing", "React Testing"],
            "cypress": ["Cypress", "Cypress.io", "E2E Testing"],
            
            # Tools & DevOps
            "git": ["Git", "GitHub", "GitLab", "Bitbucket", "Version Control", "VCS", "Source Control"],
            "github": ["GitHub", "Git Hub", "GH"],
            "gitlab": ["GitLab", "Git Lab", "GL"],
            "jenkins": ["Jenkins", "Jenkins CI", "Jenkins Pipeline"],
            "jira": ["Jira", "JIRA", "Atlassian", "Jira Software", "Project Management"],
            "confluence": ["Confluence", "Atlassian Confluence", "Wiki"],
            "postman": ["Postman", "Postman API", "API Testing"],
            "vscode": ["VS Code", "Visual Studio Code", "VSCode"],
            "intellij": ["IntelliJ", "IntelliJ IDEA", "Idea"],
            "eclipse": ["Eclipse", "Eclipse IDE"],
            
            # Soft skills
            "communication": ["Communication", "Verbal Communication", "Written Communication", "Presentation", "Interpersonal", "Communication Skills"],
            "leadership": ["Leadership", "Team Lead", "Mentoring", "Team Management", "Project Lead", "Leading Teams"],
            "problem solving": ["Problem Solving", "Analytical", "Critical Thinking", "Troubleshooting", "Debugging", "Problem-Solving"],
            "teamwork": ["Teamwork", "Collaboration", "Cross-functional", "Team Player", "Team Work"],
            "project management": ["Project Management", "Agile", "Scrum", "Kanban", "Waterfall", "PM"],
            "agile": ["Agile", "Agile Methodology", "Scrum", "Kanban", "Agile Development"],
            "scrum": ["Scrum", "Scrum Master", "Agile Scrum"],
            
            # Mobile Development
            "android": ["Android", "Android Development", "Android Studio", "Kotlin", "Java Android"],
            "ios": ["iOS", "iPhone", "iPad", "iOS Development", "Swift", "Objective-C"],
            "kotlin": ["Kotlin", "Kotlin Android", "Kotlin Multiplatform"],
            "swift": ["Swift", "Swift iOS", "SwiftUI"],
            "flutter": ["Flutter", "Flutter Dev", "Dart", "Flutter SDK"],
            "react native": ["React Native", "RN", "React Native Mobile"],
            
            # Frontend
            "html": ["HTML", "HTML5", "Hypertext Markup Language"],
            "css": ["CSS", "CSS3", "Cascading Style Sheets", "SCSS", "SASS", "Tailwind", "Bootstrap"],
            "bootstrap": ["Bootstrap", "Bootstrap 4", "Bootstrap 5", "Twitter Bootstrap"],
            "tailwind": ["Tailwind", "Tailwind CSS", "Tailwind"],
            "jquery": ["jQuery", "jQuery UI", "jQuery Mobile"],
            
            # Backend
            "rest": ["REST", "REST API", "RESTful", "RESTful API", "REST APIs"],
            "api": ["API", "APIs", "REST API", "GraphQL", "Web API"],
            "microservices": ["Microservices", "Micro-services", "Micro services"],
            "graphql": ["GraphQL", "Graph QL", "Apollo"],
            
            # Indian Specific
            "tcs": ["TCS", "Tata Consultancy Services", "Tata Consultancy"],
            "infosys": ["Infosys", "Infy"],
            "wipro": ["Wipro", "Wipro Technologies"],
            "hcl": ["HCL", "HCL Technologies"],
            "tech mahindra": ["Tech Mahindra", "TechMahindra"],
            "accenture": ["Accenture", "Accenture India"],
            "cognizant": ["Cognizant", "CTS", "Cognizant Technology Solutions"],
            "capgemini": ["Capgemini", "Capgemini India"]
        }
        
        # Technical terms for preprocessing (expanded)
        self.tech_terms = set()
        for category, synonyms in self.skill_synonyms.items():
            self.tech_terms.add(category)
            for syn in synonyms:
                self.tech_terms.add(syn.lower())
        
        # Cache for embeddings to avoid recomputation
        self.embedding_cache = {}
    
    def preprocess_text(self, text):
        """Clean and preprocess text for better embeddings"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Preserve technical terms that might have dots (like node.js)
        for term in self.tech_terms:
            if '.' in term:
                text = text.replace(term, term.replace('.', '_dot_'))
        
        # Remove special characters but keep technical terms
        text = re.sub(r'[^a-z0-9\s\.]', ' ', text)
        
        # Restore dots for technical terms
        for term in self.tech_terms:
            if '.' in term:
                text = text.replace(term.replace('.', '_dot_'), term)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def get_embedding(self, text):
        """Get embedding for text with caching"""
        # Preprocess
        cleaned = self.preprocess_text(text)
        
        # Check cache (using hash of first 1000 chars for performance)
        cache_key = hash(cleaned[:1000])
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Generate embedding
        embedding = self.model.encode(cleaned[:5000])  # Limit length
        self.embedding_cache[cache_key] = embedding
        return embedding
    
    def calculate_semantic_similarity(self, resume_text, job_text):
        """Calculate semantic similarity between resume and job description"""
        if not resume_text or not job_text:
            return 0.0
        
        # Get embeddings
        resume_emb = self.get_embedding(resume_text)
        job_emb = self.get_embedding(job_text)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([resume_emb], [job_emb])[0][0]
        
        # Scale to 0-1 range (cosine similarity ranges from -1 to 1)
        normalized = (similarity + 1) / 2
        
        return float(normalized)
    
    def find_similar_skills(self, skill, text, threshold=0.6):
        """Enhanced skill matching with synonyms"""
        if not skill or not text:
            return False
        
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        # Direct match
        if skill_lower in text_lower:
            return True
        
        # Check synonyms
        for base_skill, synonyms in self.skill_synonyms.items():
            # Check if the skill matches this category
            if skill_lower in base_skill or any(s.lower() in skill_lower for s in synonyms):
                # Check if any synonym appears in text
                if any(syn.lower() in text_lower for syn in synonyms[:5]):
                    return True
        
        # Try semantic similarity for unmatched
        try:
            skill_emb = self.get_embedding(skill)
            text_emb = self.get_embedding(text[:1000])
            similarity = cosine_similarity([skill_emb], [text_emb])[0][0]
            normalized = (similarity + 1) / 2
            return normalized > threshold
        except Exception as e:
            print(f"Semantic similarity error: {e}")
            return False
    
    def extract_key_phrases(self, text, top_k=5):
        """Extract most important phrases using embeddings"""
        if not text:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        if not sentences:
            return []
        
        # Get embeddings for all sentences
        sent_embeddings = self.model.encode(sentences[:20])  # Limit for performance
        doc_embedding = self.get_embedding(text)
        
        # Calculate similarity scores
        scores = cosine_similarity([doc_embedding], sent_embeddings)[0]
        
        # Get top sentences
        top_indices = np.argsort(scores)[-top_k:][::-1]
        key_phrases = [sentences[i][:100] for i in top_indices]
        
        return key_phrases
    
    def calculate_component_scores(self, resume_data, job_text):
        """Calculate semantic scores for different resume components"""
        scores = {}
        
        # Overall similarity
        scores['overall'] = self.calculate_semantic_similarity(
            resume_data.get('raw_text', ''), 
            job_text
        )
        
        # Section-wise similarity
        sections = resume_data.get('sections', {})
        for section in ['summary', 'experience', 'skills', 'education']:
            section_text = sections.get(section, '')
            if section_text:
                scores[f'section_{section}'] = self.calculate_semantic_similarity(
                    section_text, 
                    job_text
                )
        
        return scores
    
    def get_skill_categories(self):
        """Return all skill categories for reference"""
        return list(self.skill_synonyms.keys())
    
    def get_synonyms_for_skill(self, skill):
        """Get all synonyms for a given skill"""
        skill_lower = skill.lower()
        for base_skill, synonyms in self.skill_synonyms.items():
            if skill_lower in base_skill or any(s.lower() in skill_lower for s in synonyms):
                return [base_skill] + synonyms[:8]
        return [skill]

# Singleton instance for reuse
_semantic_matcher = None

def get_semantic_matcher():
    """Get or create the semantic matcher singleton"""
    global _semantic_matcher
    if _semantic_matcher is None:
        _semantic_matcher = SemanticMatcher()
    return _semantic_matcher