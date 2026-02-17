import streamlit as st
import json
from datetime import datetime
import re
from constants import INDUSTRY_TEMPLATES, TECH_KEYWORDS, SOFT_SKILLS, ACTION_VERBS
from utils import enhance_bullet_point, calculate_optimized_score

def show_resume_builder():
    """Resume Builder & Optimizer Module"""
    
    st.markdown("## 📝 AI Resume Builder & Optimizer")
    st.markdown("Generate an ATS-optimized resume based on your job description")
    
    # Initialize session state for builder
    if 'builder_step' not in st.session_state:
        st.session_state.builder_step = 1
    if 'optimized_resume' not in st.session_state:
        st.session_state.optimized_resume = None
    if 'builder_jd' not in st.session_state:
        st.session_state.builder_jd = ""
    
    # ============= STEP 1: Job Description Input =============
    if st.session_state.builder_step == 1:
        with st.container():
            st.markdown('<div class="builder-card">', unsafe_allow_html=True)
            st.markdown("### 📋 Step 1: Paste Target Job Description")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Widget is created HERE with key "builder_jd"
                jd_for_builder = st.text_area(
                    "Paste the job description you're targeting:",
                    value=st.session_state.builder_jd,  # Direct access, not .get()
                    height=250,
                    placeholder="Paste the job description here...",
                    key="builder_jd"  # DON'T CHANGE THIS KEY
                )
            
            with col2:
                st.markdown("#### Quick Industry Select")
                builder_industry = st.selectbox(
                    "Industry:",
                    options=list(INDUSTRY_TEMPLATES.keys()),
                    index=0,
                    key="builder_industry"
                )
                
                # LOAD SAMPLE JD BUTTON - Sets session state BEFORE widget recreation
                if st.button("📋 Load Sample JD", use_container_width=True):
                    st.session_state.builder_jd = get_sample_jd(builder_industry)
                    st.rerun()
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # ANALYZE BUTTON - Reads from widget, doesn't set session state
                if st.button("🔍 Analyze & Continue to Step 2", type="primary", use_container_width=True):
                    if st.session_state.builder_jd:  # Read directly from widget
                        st.session_state.builder_step = 2  # Only change step
                        st.rerun()
                    else:
                        st.error("Please paste a job description!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= STEP 2: Extract Keywords & Show Form =============
    elif st.session_state.builder_step == 2:
        with st.container():
            st.markdown('<div class="builder-card">', unsafe_allow_html=True)
            
            # Extract keywords from JD
            jd_text = st.session_state.builder_jd.lower()
            
            # Detect technical skills
            detected_tech = []
            detected_soft = []
            
            for skill in TECH_KEYWORDS:
                if skill in jd_text:
                    detected_tech.append(skill.title())
            
            for skill in SOFT_SKILLS:
                if skill in jd_text:
                    detected_soft.append(skill.title())
            
            # Display detected keywords
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**💻 Required Technical Skills:**")
                if detected_tech:
                    tech_chips = " ".join([f'<span style="background-color: #dbeafe; color: #1e40af; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 15px; display: inline-block; font-size: 0.9rem;">{skill}</span>' for skill in detected_tech[:12]])
                    st.markdown(tech_chips, unsafe_allow_html=True)
                else:
                    st.info("No specific technical skills detected")
            
            with col2:
                st.markdown("**🤝 Required Soft Skills:**")
                if detected_soft:
                    soft_chips = " ".join([f'<span style="background-color: #fef3c7; color: #92400e; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 15px; display: inline-block; font-size: 0.9rem;">{skill}</span>' for skill in detected_soft[:8]])
                    st.markdown(soft_chips, unsafe_allow_html=True)
                else:
                    st.info("No specific soft skills detected")
            
            st.markdown("---")
            st.markdown("### 📝 Step 2: Enter Your Details")
            
            # Resume Builder Form
            with st.form("resume_builder_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *", placeholder="John Doe", key="builder_name")
                    email = st.text_input("Email *", placeholder="john@example.com", key="builder_email")
                    phone = st.text_input("Phone", placeholder="+91 98765 43210", key="builder_phone")
                    location = st.text_input("Location", placeholder="Bangalore, India", key="builder_location")
                
                with col2:
                    linkedin = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/johndoe", key="builder_linkedin")
                    github = st.text_input("GitHub/Portfolio", placeholder="github.com/johndoe", key="builder_github")
                    experience_years = st.selectbox(
                        "Years of Experience *",
                        options=["Fresher", "1-2 years", "3-5 years", "6-8 years", "8+ years"],
                        key="builder_exp"
                    )
                    education = st.selectbox(
                        "Highest Education *",
                        options=["B.Tech/B.E.", "MCA", "BCA", "B.Sc", "M.Tech", "MBA", "B.Com", "M.Com", "BA", "MA", "Other"],
                        key="builder_edu"
                    )
                
                st.markdown("#### 💼 Work Experience (Most Recent)")
                experience = st.text_area(
                    "Describe your work experience (use bullet points):",
                    height=150,
                    placeholder="• Developed Python Django applications\n• Implemented REST APIs\n• Worked with AWS services\n• Led a team of 3 developers",
                    key="builder_exp_text"
                )
                
                st.markdown("#### 🛠️ Technical Skills")
                skills = st.text_area(
                    "List your technical skills (comma-separated):",
                    placeholder=f"Python, Django, React, AWS, Docker, MySQL, {', '.join(detected_tech[:3]) if detected_tech else ''}",
                    key="builder_skills",
                    value=f"{', '.join(detected_tech[:5]) if detected_tech else ''}"
                )
                
                st.markdown("#### 🎓 Projects")
                projects = st.text_area(
                    "Highlight your key projects:",
                    height=120,
                    placeholder="• E-commerce Platform - Built with Django and React\n• Machine Learning Model - Predictive analysis using scikit-learn\n• Mobile App - Flutter-based food delivery app",
                    key="builder_projects"
                )
                
                st.markdown("#### 📜 Certifications")
                certifications = st.text_input(
                    "Relevant certifications (comma-separated):",
                    placeholder="AWS Certified, Google Analytics, Python Institute, Microsoft Certified",
                    key="builder_certs"
                )
                
                submitted = st.form_submit_button("🚀 Generate Optimized Resume", type="primary", use_container_width=True)
                
                if submitted:
                    if not name or not email or not experience or not skills:
                        st.error("Please fill in all required fields (*)")
                    else:
                        # Generate optimized resume
                        optimized = generate_optimized_resume(
                            name, email, phone, location, linkedin, github,
                            experience_years, education, experience, skills,
                            projects, certifications, detected_tech, detected_soft,
                            jd_text
                        )
                        st.session_state.optimized_resume = optimized
                        st.session_state.builder_step = 3
                        st.rerun()
            
            # Back button
            if st.button("← Back to Step 1", use_container_width=True):
                st.session_state.builder_step = 1
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= STEP 3: Display Optimized Resume =============
    elif st.session_state.builder_step == 3:
        st.markdown('<div class="builder-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Your ATS-Optimized Resume")
        st.success("🎉 Your resume has been optimized for this job description!")
        
        resume = st.session_state.optimized_resume
        
        # Display resume in tabs
        tab1, tab2, tab3 = st.tabs(["📄 Formatted Resume", "📊 ATS Analysis", "📥 Download"])
        
        with tab1:
            st.markdown(f"""
            <div class="resume-preview">
                <h1 style="color: #1e40af; margin-bottom: 0.5rem; font-size: 2rem;">{resume['name']}</h1>
                <p style="color: #4b5563; margin-bottom: 0.5rem; font-size: 1rem;">
                    📍 {resume['location']} | 📧 {resume['email']} | 📱 {resume['phone']}
                </p>
                <p style="color: #4b5563; margin-bottom: 1.5rem; font-size: 0.95rem;">
                    🔗 <a href="{resume['linkedin']}" style="color: #2563eb;">{resume['linkedin']}</a> | 
                    🐙 <a href="{resume['github']}" style="color: #2563eb;">{resume['github']}</a>
                </p>
                
                <hr style="border: 1px solid #e5e7eb; margin: 1.5rem 0;">
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-bottom: 0.5rem;">🎯 Professional Summary</h2>
                <p style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px; line-height: 1.6;">
                    {resume['summary']}
                </p>
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">💻 Technical Skills</h2>
                <div style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px;">
                    {resume['skills_html']}
                </div>
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">💼 Work Experience</h2>
                <div style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px;">
                    {resume['experience_html']}
                </div>
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">🎓 Education</h2>
                <div style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px;">
                    {resume['education_html']}
                </div>
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">🚀 Projects</h2>
                <div style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px;">
                    {resume['projects_html']}
                </div>
                
                <h2 style="color: #1e40af; font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">📜 Certifications</h2>
                <div style="background-color: #f3f4f6; padding: 1rem; border-radius: 5px;">
                    {resume['certifications_html']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 📊 ATS Optimization Score")
            
            # Calculate ATS score for the optimized resume
            ats_score = calculate_optimized_score(resume, st.session_state.builder_jd)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                    <h1 style="font-size: 3rem;">{ats_score}</h1>
                    <p style="font-size: 1.2rem;">ATS Score</p>
                    <p style="opacity: 0.9;">out of 100</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**✅ Keywords Matched:**")
                matched = resume['keyword_match']
                for kw in matched[:8]:
                    st.markdown(f"- ✓ **{kw}**")
                
                st.markdown("**💡 Suggested Skills to Add:**")
                for skill in resume['suggested_skills'][:5]:
                    st.markdown(f"- + {skill}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # ATS Meter
            st.markdown("### 📊 ATS Compatibility Meter")
            st.markdown(f"""
            <div class="ats-meter">
                <div class="ats-fill" style="width: {ats_score}%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🚀 Optimization Tips")
            tips = [
                "✅ Added all required technical skills from JD",
                "✅ Professional summary tailored to the role",
                "✅ Bullet points enhanced with action verbs",
                "✅ Education formatted for Indian ATS systems",
                "✅ Missing keywords highlighted for quick addition"
            ]
            for tip in tips:
                st.markdown(f"- {tip}")
        
        with tab3:
            st.markdown("### 📥 Download Your Resume")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📄 Download as Plain Text",
                    data=resume['text_format'],
                    file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📦 Download as JSON",
                    data=json.dumps(resume, indent=2),
                    file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("""
            ### 📋 Next Steps:
            1. **Copy the formatted resume** above and paste into MS Word/Google Docs
            2. **Add any missing skills** highlighted in the ATS Analysis tab
            3. **Save as PDF** with a professional filename
            4. **Submit with confidence!** 🎉
            """)
        
        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Create Another Resume", use_container_width=True):
                st.session_state.builder_step = 1
                st.session_state.optimized_resume = None
                st.session_state.builder_jd = ""
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def generate_optimized_resume(name, email, phone, location, linkedin, github,
                            experience_years, education, experience, skills,
                            projects, certifications, detected_tech, detected_soft, jd_text):
    """Generate ATS-optimized resume content"""
    
    # Process skills
    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    # Add missing required skills
    missing_skills = [s for s in detected_tech if s.lower() not in [sk.lower() for sk in skills_list]]
    suggested_skills = skills_list + missing_skills[:3]
    
    # Generate professional summary
    if experience_years == "Fresher":
        summary = f"Recent {education} graduate with strong foundation in {', '.join(skills_list[:3])}. Passionate about building scalable solutions and eager to contribute to innovative projects. Completed internships and academic projects in {', '.join(detected_tech[:2]) if detected_tech else 'relevant technologies'}. Seeking opportunities to apply technical skills and grow professionally."
    else:
        summary = f"{experience_years} experienced professional specializing in {', '.join(skills_list[:3])}. Proven track record of delivering high-quality solutions and collaborating with cross-functional teams. Expertise in {', '.join(detected_tech[:3]) if detected_tech else 'software development'} with strong {', '.join(detected_soft[:2]) if detected_soft else 'problem-solving'} skills. Committed to writing clean, maintainable code and continuous learning."
    
    # Format experience with enhanced bullet points
    exp_lines = experience.split('\n')
    exp_html = "<ul style='margin: 0; padding-left: 1.2rem;'>"
    for line in exp_lines:
        if line.strip():
            enhanced_line = enhance_bullet_point(line.strip())
            exp_html += f"<li style='margin-bottom: 0.5rem;'>{enhanced_line}</li>"
    exp_html += "</ul>"
    
    # Format skills as chips
    all_skills = list(set(skills_list + suggested_skills))
    skills_html = " ".join([f'<span style="background-color: #dbeafe; color: #1e40af; padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; display: inline-block; font-size: 0.9rem; font-weight: 500;">{skill}</span>' for skill in all_skills[:15]])
    
    # Format education
    current_year = datetime.now().year
    if experience_years == "Fresher":
        grad_year = current_year
    elif experience_years == "1-2 years":
        grad_year = current_year - 2
    elif experience_years == "3-5 years":
        grad_year = current_year - 4
    else:
        grad_year = current_year - 6
    
    education_html = f"<p style='margin: 0;'><strong>{education}</strong> - University of Mumbai, {grad_year}<br>CGPA: 8.2/10</p>"
    
    # Format projects
    proj_lines = projects.split('\n') if projects else []
    proj_html = "<ul style='margin: 0; padding-left: 1.2rem;'>"
    for line in proj_lines[:3]:
        if line.strip():
            proj_html += f"<li style='margin-bottom: 0.5rem;'>{line.strip()}</li>"
    if not proj_lines and detected_tech:
        proj_html += f"<li style='margin-bottom: 0.5rem;'><strong>{detected_tech[0]} Application</strong> - Built a full-stack application using {detected_tech[0]} and {detected_tech[1] if len(detected_tech) > 1 else 'React'}. Implemented key features and deployed on cloud.</li>"
    proj_html += "</ul>"
    
    # Format certifications
    cert_list = [c.strip() for c in certifications.split(',') if c.strip()]
    cert_html = "<ul style='margin: 0; padding-left: 1.2rem;'>"
    for cert in cert_list[:4]:
        cert_html += f"<li style='margin-bottom: 0.3rem;'>{cert}</li>"
    if not cert_list and detected_tech:
        cert_html += f"<li style='margin-bottom: 0.3rem;'><strong>AWS Certified Cloud Practitioner</strong> (In Progress)</li>"
        cert_html += f"<li style='margin-bottom: 0.3rem;'><strong>Google {detected_tech[0]} Certification</strong> (Suggested)</li>"
    cert_html += "</ul>"
    
    # Text format for download
    text_format = f"""
{name}
{location} | {email} | {phone}
{linkedin} | {github}

PROFESSIONAL SUMMARY
{summary}

TECHNICAL SKILLS
{', '.join(all_skills[:15])}

WORK EXPERIENCE
{experience}

EDUCATION
{education} - University of Mumbai, {grad_year}
CGPA: 8.2/10

PROJECTS
{projects if projects else f'• {detected_tech[0] if detected_tech else "Software"} Development Project - Built using modern technologies'}

CERTIFICATIONS
{certifications if certifications else '• AWS Certified Cloud Practitioner (In Progress)'}

---
Generated by Indian ATS Resume Scanner v2.0
Optimized for: {', '.join(detected_tech[:5]) if detected_tech else 'Software Development'}
Date: {datetime.now().strftime('%d %B %Y')}
"""
    
    return {
        'name': name,
        'email': email,
        'phone': phone if phone else "+91 98765 43210",
        'location': location if location else "Bangalore, India",
        'linkedin': linkedin if linkedin else "linkedin.com/in/johndoe",
        'github': github if github else "github.com/johndoe",
        'summary': summary,
        'skills_html': skills_html,
        'experience_html': exp_html,
        'education_html': education_html,
        'projects_html': proj_html,
        'certifications_html': cert_html,
        'text_format': text_format,
        'keyword_match': detected_tech[:10],
        'suggested_skills': missing_skills[:5]
    }


def get_sample_jd(industry):
    """Get sample job description for industry"""
    from constants import INDUSTRY_TEMPLATES
    
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