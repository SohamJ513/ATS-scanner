# ============================================
# COMPANY_TEMPLATES.PY - Indian Company ATS Simulator
# ============================================

COMPANY_REQUIREMENTS = {
    "TCS Ninja": {
        "description": "TCS Ninja (National Qualifier Test) - Entry Level",
        "skills": {
            "critical": ["Python", "Java", "C++", "SQL", "DBMS", "Data Structures", "Algorithms"],
            "preferred": ["Operating Systems", "Computer Networks", "OOPS", "Aptitude"],
            "bonus": ["Cloud Basics", "Git", "Problem Solving"]
        },
        "education": ["B.Tech", "MCA", "BCA", "B.Sc CS"],
        "cgpa_cutoff": 6.0,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "Moderate",
        "keywords": ["ntt", "ninja", "digital", "campus", "fresher"],
        "icon": "🔵"
    },
    
    "TCS Digital": {
        "description": "TCS Digital - Premium Role, Higher Package",
        "skills": {
            "critical": ["Advanced DSA", "System Design", "Python/Java Advanced", "DBMS", "Operating Systems"],
            "preferred": ["Cloud Computing", "Microservices", "DevOps", "Machine Learning"],
            "bonus": ["Research Papers", "Open Source Contributions", "Hackathon Wins"]
        },
        "education": ["B.Tech", "M.Tech", "MCA"],
        "cgpa_cutoff": 7.5,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "High",
        "keywords": ["digital", "premium", "advanced", "ninja", "ilu"],
        "icon": "💎"
    },
    
    "Infosys": {
        "description": "Infosys - System Engineer / Specialist Programmer",
        "skills": {
            "critical": ["Python", "Java", "SQL", "Data Structures", "Web Technologies"],
            "preferred": ["Spring Boot", "Django", "React", "AWS Basics"],
            "bonus": ["Certifications", "Internships", "Soft Skills"]
        },
        "education": ["B.Tech", "MCA", "BCA", "B.Sc CS"],
        "cgpa_cutoff": 6.0,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "High",
        "keywords": ["infy", "system engineer", "specialist", "hackwithinfy"],
        "icon": "🟣"
    },
    
    "Infosys Power Programmer": {
        "description": "Infosys Power Programmer - High Package",
        "skills": {
            "critical": ["Advanced DSA", "Competitive Programming", "System Design", "Multiple Languages"],
            "preferred": ["CP Ratings", "CodeChef/Codeforces", "Hackathon Wins"],
            "bonus": ["Open Source", "Research", "Patents"]
        },
        "education": ["B.Tech", "M.Tech"],
        "cgpa_cutoff": 8.0,
        "coding_round": True,
        "aptitude_round": False,
        "communication": "Moderate",
        "keywords": ["power programmer", "specialist", "hackwithinfy", "cpp"],
        "icon": "⚡"
    },
    
    "Wipro": {
        "description": "Wipro - Elite / Turbo",
        "skills": {
            "critical": ["C", "Java", "SQL", "Data Structures", "Manual Testing"],
            "preferred": ["Selenium", "Automation", "Web Development"],
            "bonus": ["Certifications", "Communication Skills"]
        },
        "education": ["B.Tech", "MCA", "BCA", "B.Sc CS"],
        "cgpa_cutoff": 6.0,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "High",
        "keywords": ["elite", "turbo", "wipro", "campus"],
        "icon": "🟢"
    },
    
    "Wipro Turbo": {
        "description": "Wipro Turbo - Premium Role",
        "skills": {
            "critical": ["Advanced Java", "Spring", "Hibernate", "Microservices", "Cloud Basics"],
            "preferred": ["AWS/Azure", "DevOps", "Docker", "Kubernetes"],
            "bonus": ["Project Experience", "Certifications", "Hackathons"]
        },
        "education": ["B.Tech", "M.Tech"],
        "cgpa_cutoff": 7.0,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "High",
        "keywords": ["turbo", "elite", "premium", "wipro"],
        "icon": "🚀"
    },
    
    "Amazon India": {
        "description": "Amazon - SDE (Software Development Engineer)",
        "skills": {
            "critical": ["DSA", "System Design", "OOP", "Any OOP Language", "Problem Solving"],
            "preferred": ["Distributed Systems", "Cloud (AWS)", "Scalability", "Low Level Design"],
            "bonus": ["Leadership", "Bar Raiser", "Previous Experience"]
        },
        "education": ["B.Tech", "M.Tech", "MCA"],
        "cgpa_cutoff": 7.0,
        "coding_round": True,
        "aptitude_round": False,
        "communication": "Very High",
        "keywords": ["amazon", "sde", "aws", "leadership", "bar raiser"],
        "icon": "🟠"
    },
    
    "Google India": {
        "description": "Google - SDE / SWE",
        "skills": {
            "critical": ["Advanced DSA", "System Design", "Algorithms", "C++/Java/Python"],
            "preferred": ["Distributed Systems", "Compilers", "OS", "Networking"],
            "bonus": ["Published Research", "CP Ratings", "Open Source"]
        },
        "education": ["B.Tech", "M.Tech", "PhD"],
        "cgpa_cutoff": 8.0,
        "coding_round": True,
        "aptitude_round": False,
        "communication": "Very High",
        "keywords": ["google", "swe", "sde", "mountain view", "bangalore"],
        "icon": "🔴"
    },
    
    "Microsoft India": {
        "description": "Microsoft - SDE",
        "skills": {
            "critical": ["DSA", "System Design", "C#/.NET", "Azure", "Problem Solving"],
            "preferred": ["Cloud Computing", "Microservices", "Design Patterns"],
            "bonus": ["Microsoft Certifications", "Hackathons", "Open Source"]
        },
        "education": ["B.Tech", "M.Tech", "MCA"],
        "cgpa_cutoff": 7.5,
        "coding_round": True,
        "aptitude_round": False,
        "communication": "High",
        "keywords": ["microsoft", "azure", "sde", "bing", "hyderabad"],
        "icon": "🔵"
    },
    
    "Accenture": {
        "description": "Accenture - Associate Software Engineer",
        "skills": {
            "critical": ["Any Programming Language", "SQL", "Data Structures", "Communication"],
            "preferred": ["Cloud Basics", "Testing", "Agile"],
            "bonus": ["Certifications", "Internships"]
        },
        "education": ["B.Tech", "MCA", "BCA", "B.Sc CS", "B.Com", "BA"],
        "cgpa_cutoff": 6.0,
        "coding_round": False,
        "aptitude_round": True,
        "communication": "Very High",
        "keywords": ["accenture", "ase", "campus", "fresher"],
        "icon": "🟣"
    },
    
    "Cognizant": {
        "description": "Cognizant - Programmer Analyst",
        "skills": {
            "critical": ["Java/.NET", "SQL", "Data Structures", "Communication"],
            "preferred": ["Web Technologies", "Testing", "Agile"],
            "bonus": ["Certifications", "Internships"]
        },
        "education": ["B.Tech", "MCA", "BCA", "B.Sc CS"],
        "cgpa_cutoff": 6.0,
        "coding_round": True,
        "aptitude_round": True,
        "communication": "High",
        "keywords": ["cognizant", "cts", "programmer analyst", "genc"],
        "icon": "🟢"
    }
}

def calculate_company_score(resume_skills, company_name, cgpa, experience_years):
    """Calculate company-specific ATS score"""
    
    company = COMPANY_REQUIREMENTS.get(company_name)
    if not company:
        return 0, ["Company not found"]
    
    score = 0
    max_score = 100
    details = []
    
    # Convert resume skills to lowercase for matching
    resume_skills_lower = [s.lower() for s in resume_skills]
    resume_text = ' '.join(resume_skills_lower)
    
    # Skill Match (50 points)
    critical_skills = company["skills"]["critical"]
    preferred_skills = company["skills"]["preferred"]
    bonus_skills = company["skills"]["bonus"]
    
    # Critical skills (30 points)
    critical_match = 0
    for skill in critical_skills:
        skill_lower = skill.lower()
        if any(skill_lower in s for s in resume_skills_lower):
            critical_match += 1
            details.append(f"✅ {skill} - Critical skill matched")
    
    critical_score = (critical_match / len(critical_skills)) * 30
    score += critical_score
    
    # Preferred skills (15 points)
    preferred_match = 0
    for skill in preferred_skills:
        skill_lower = skill.lower()
        if any(skill_lower in s for s in resume_skills_lower):
            preferred_match += 1
            details.append(f"✓ {skill} - Preferred skill matched")
    
    if preferred_skills:
        preferred_score = (preferred_match / len(preferred_skills)) * 15
        score += preferred_score
    
    # Bonus skills (5 points)
    bonus_match = 0
    for skill in bonus_skills:
        skill_lower = skill.lower()
        if any(skill_lower in s for s in resume_skills_lower):
            bonus_match += 1
            details.append(f"+ {skill} - Bonus skill matched")
    
    if bonus_skills:
        bonus_score = (bonus_match / len(bonus_skills)) * 5
        score += bonus_score
    
    # CGPA Check (10 points)
    try:
        cgpa_float = float(cgpa)
        if cgpa_float >= company["cgpa_cutoff"]:
            score += 10
            details.append(f"✅ CGPA {cgpa_float} meets cutoff of {company['cgpa_cutoff']}")
        else:
            details.append(f"⚠️ CGPA {cgpa_float} below cutoff of {company['cgpa_cutoff']}")
    except:
        details.append(f"⚠️ Invalid CGPA value")
    
    # Experience Check (10 points)
    try:
        exp = int(experience_years)
        if "fresher" in company_name.lower() or "ninja" in company_name.lower():
            if exp <= 1:
                score += 10
                details.append(f"✅ Fresher role - {exp} years experience")
            else:
                score += 5
                details.append(f"⚠️ Overqualified for fresher role ({exp} years)")
        else:
            if exp >= 1:
                score += 10
                details.append(f"✅ Experience: {exp} years")
            else:
                score += 2
                details.append(f"⚠️ Fresher applying for experienced role")
    except:
        details.append(f"⚠️ Invalid experience value")
    
    # Communication (10 points)
    comm_keywords = ["communication", "presentation", "client", "team lead", "mentor", "soft skills"]
    if company["communication"] == "Very High":
        if any(kw in resume_text for kw in comm_keywords):
            score += 10
            details.append("✅ Strong communication skills detected")
        else:
            score += 4
            details.append("⚠️ Add communication skills to resume")
    elif company["communication"] == "High":
        if any(kw in resume_text for kw in comm_keywords[:3]):
            score += 8
            details.append("✓ Communication skills present")
        else:
            score += 5
            details.append("⚠️ Communication skills recommended")
    else:
        score += 6
        details.append("✓ Basic communication assumed")
    
    # Coding Round (5 points)
    if company["coding_round"]:
        dsa_keywords = ["dsa", "data structure", "algorithm", "leetcode", "hackerrank", "codechef", "coding"]
        if any(kw in resume_text for kw in dsa_keywords):
            score += 5
            details.append("✅ DSA/Coding practice mentioned")
        else:
            score += 1
            details.append("⚠️ Add DSA preparation to resume")
    
    # Aptitude (5 points)
    if company["aptitude_round"]:
        aptitude_keywords = ["aptitude", "quantitative", "logical", "reasoning", "math"]
        if any(kw in resume_text for kw in aptitude_keywords):
            score += 5
            details.append("✅ Aptitude skills mentioned")
        else:
            score += 1
            details.append("⚠️ Aptitude practice recommended")
    
    return min(round(score, 1), 100), details[:8]  # Return top 8 details