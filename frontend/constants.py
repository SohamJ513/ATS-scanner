# ============================================
# CONSTANTS.PY - All templates, keywords, and static data
# ============================================

# Industry Templates
INDUSTRY_TEMPLATES = {
    "All Industries": {"skills": [], "degrees": []},
    "💻 IT/Software": {
        "skills": ["Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker", "Git", "SQL", "MongoDB"],
        "degrees": ["B.Tech", "MCA", "BCA", "B.E.", "M.Tech"],
        "keywords": ["agile", "scrum", "rest api", "microservices", "cloud", "devops", "full stack"]
    },
    "🏦 Banking/Finance": {
        "skills": ["Financial Analysis", "Risk Management", "Excel", "Tally", "SAP", "Bloomberg", "CFA", "MBA"],
        "degrees": ["B.Com", "M.Com", "MBA", "CA", "CFA", "BBA"],
        "keywords": ["portfolio management", "investment banking", "audit", "taxation", "financial modeling"]
    },
    "🏭 Manufacturing": {
        "skills": ["AutoCAD", "SolidWorks", "Six Sigma", "Lean Manufacturing", "Supply Chain", "ERP", "SAP"],
        "degrees": ["B.E.", "B.Tech", "Diploma", "ME", "M.Tech"],
        "keywords": ["quality control", "production planning", "inventory management", "process improvement"]
    },
    "🏛️ Government/PSU": {
        "skills": ["Public Administration", "Policy Analysis", "Governance", "GATE", "UPSC", "SSC"],
        "degrees": ["BA", "MA", "LLB", "B.Tech", "MBA"],
        "keywords": ["civil services", "public sector", "government projects", "administrative"]
    },
    "📊 Data Science/AI": {
        "skills": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Tableau"],
        "degrees": ["B.Tech", "M.Tech", "M.Sc", "BCA", "MCA"],
        "keywords": ["data visualization", "statistical analysis", "predictive modeling", "NLP", "computer vision"]
    },
    "📱 Mobile Development": {
        "skills": ["Android", "iOS", "Kotlin", "Swift", "Flutter", "React Native", "Java", "Objective-C"],
        "degrees": ["B.Tech", "BCA", "MCA", "B.Sc IT"],
        "keywords": ["mobile ui", "app store", "google play", "mobile architecture", "push notifications"]
    }
}

# Experience Levels
EXPERIENCE_LEVELS = {
    "All Levels": 0,
    "🎓 Fresher (0-1 years)": 1,
    "🚀 Junior (1-3 years)": 2,
    "💪 Mid-Level (3-6 years)": 5,
    "👨‍💼 Senior (6-10 years)": 8,
    "👑 Lead/Manager (10+ years)": 12
}

# Tech keywords for resume builder
TECH_KEYWORDS = [
    'python', 'java', 'javascript', 'react', 'angular', 'node', 'django',
    'flask', 'spring', 'aws', 'azure', 'docker', 'kubernetes', 'sql',
    'mongodb', 'git', 'jenkins', 'machine learning', 'data science',
    'android', 'ios', 'flutter', 'html', 'css', 'rest api', 'microservices',
    'tensorflow', 'pytorch', 'pandas', 'numpy', 'tableau', 'power bi'
]

# Soft skills
SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'problem solving',
    'analytical', 'project management', 'agile', 'scrum', 'collaboration',
    'critical thinking', 'time management', 'adaptability'
]

# Action verbs for bullet points
ACTION_VERBS = {
    'developed': 'Engineered and deployed',
    'worked': 'Collaborated on',
    'made': 'Implemented',
    'helped': 'Facilitated',
    'fixed': 'Resolved critical',
    'wrote': 'Authored',
    'tested': 'Validated and tested',
    'designed': 'Architected',
    'created': 'Built',
    'managed': 'Orchestrated',
    'improved': 'Optimized',
    'handled': 'Managed'
}

# Sample Job Descriptions
def get_sample_jd(industry):
    """Get sample job description for industry"""
    if industry == "💻 IT/Software":
        return """
        We're hiring a Software Engineer with 2+ years of experience.
        
        Requirements:
        - Strong knowledge of Python and Django
        - Experience with React.js and JavaScript
        - Database skills: MySQL, MongoDB
        - Familiarity with AWS services
        - Experience with REST APIs
        - Knowledge of Git and CI/CD
        
        Preferred Qualifications:
        - B.Tech/B.E. in Computer Science
        - Experience with Docker and Kubernetes
        """
    elif industry == "🏦 Banking/Finance":
        return """
        Hiring a Financial Analyst for our Mumbai office.
        
        Requirements:
        - CA/CFA/MBA Finance preferred
        - 3+ years in financial modeling
        - Advanced Excel and Tally skills
        - Knowledge of risk management
        - Experience with SAP preferred
        
        Location: Mumbai
        """
    elif industry == "📊 Data Science/AI":
        return """
        Data Scientist with 2+ years experience.
        
        Requirements:
        - Python, SQL, Machine Learning
        - TensorFlow/PyTorch experience
        - Data visualization skills
        - Statistical analysis
        - B.Tech/M.Tech in CS or related
        
        Location: Bangalore/Hyderabad
        """
    else:
        return f"""
        {industry} position with relevant experience.
        
        Key Skills:
        {', '.join(INDUSTRY_TEMPLATES[industry]['skills'][:8])}
        
        Education:
        {', '.join(INDUSTRY_TEMPLATES[industry]['degrees'][:4])}
        
        Location: Multiple cities in India
        """