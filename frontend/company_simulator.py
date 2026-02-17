# ============================================
# COMPANY_SIMULATOR.PY - Company ATS Simulator UI
# ============================================

import streamlit as st
from company_templates import COMPANY_REQUIREMENTS, calculate_company_score

def show_company_simulator(resume_skills=None, cgpa=None, experience=None):
    """Display company-specific ATS simulator"""
    
    if resume_skills is None:
        resume_skills = []
    
    # Use provided values or get from session state
    if cgpa is None:
        cgpa = st.session_state.get('company_cgpa', 7.5)
    if experience is None:
        experience = st.session_state.get('company_exp', 0)
    
    st.markdown("## 🏢 Company-Specific ATS Simulator")
    st.markdown("Different companies use different ATS filters. See how you score at top Indian companies!")
    
    # Initialize session state for company simulator
    st.session_state.company_cgpa = cgpa
    st.session_state.company_exp = experience
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("### 📋 Your Profile")
        
        # Input fields
        cgpa_input = st.number_input(
            "Your CGPA (out of 10)", 
            min_value=0.0, 
            max_value=10.0, 
            value=float(cgpa),
            step=0.1,
            key="cgpa_input"
        )
        st.session_state.company_cgpa = cgpa_input
        
        experience_input = st.selectbox(
            "Years of Experience",
            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            index=min(experience, 10),
            key="exp_input"
        )
        st.session_state.company_exp = experience_input
        
        st.markdown("### 🛠️ Your Skills")
        
        # If skills passed from scanner, show them
        if resume_skills:
            st.success(f"✅ {len(resume_skills)} skills detected from resume")
            
            # Show skills as chips
            skills_html = " ".join([f'<span style="background-color: #dbeafe; color: #1e40af; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 15px; display: inline-block; font-size: 0.9rem;">{skill}</span>' for skill in resume_skills[:12]])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No skills provided. Enter your skills below:")
            skill_input = st.text_area(
                "Skills (comma-separated)",
                placeholder="Python, Java, SQL, Data Structures, AWS, Communication",
                height=100,
                key="skill_input"
            )
            if skill_input:
                resume_skills = [s.strip() for s in skill_input.split(',') if s.strip()]
            else:
                resume_skills = ["Python", "SQL", "Communication"]  # Default
        
        st.markdown("### 🎯 Filter Companies")
        
        # Company categories
        category = st.selectbox(
            "Company Category",
            ["All Companies", "🥇 Top Tier (Amazon, Google, Microsoft)", 
             "🥈 Mid Tier (TCS Digital, Infosys PP, Wipro Turbo)",
             "🎓 Fresher Friendly (TCS Ninja, Accenture, Cognizant)"],
            key="company_category"
        )
    
    with col2:
        # Filter companies based on category
        filtered_companies = []
        if category == "All Companies":
            filtered_companies = list(COMPANY_REQUIREMENTS.keys())
        elif "Top Tier" in category:
            top_tier = ["Amazon India", "Google India", "Microsoft India", "TCS Digital", "Infosys Power Programmer", "Wipro Turbo"]
            filtered_companies = [c for c in top_tier if c in COMPANY_REQUIREMENTS]
        elif "Mid Tier" in category:
            mid_tier = ["TCS Digital", "Infosys Power Programmer", "Wipro Turbo"]
            filtered_companies = [c for c in mid_tier if c in COMPANY_REQUIREMENTS]
        else:
            fresher = ["TCS Ninja", "Infosys", "Wipro", "Accenture", "Cognizant"]
            filtered_companies = [c for c in fresher if c in COMPANY_REQUIREMENTS]
        
        if filtered_companies:
            st.markdown("### 📊 Company Scores")
            
            # Create score cards for each company
            scores = []
            for company in filtered_companies[:6]:  # Show top 6
                score, details = calculate_company_score(
                    resume_skills, 
                    company, 
                    cgpa_input, 
                    experience_input
                )
                scores.append((company, score, details))
            
            # Sort by score descending
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Display as cards
            for company, score, details in scores:
                company_data = COMPANY_REQUIREMENTS[company]
                icon = company_data.get('icon', '🏢')
                
                # Determine color based on score
                if score >= 80:
                    color = "#10b981"
                    badge = "🔥 Hot"
                elif score >= 60:
                    color = "#f59e0b"
                    badge = "📈 Good"
                else:
                    color = "#6b7280"
                    badge = "🎯 Needs Work"
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; 
                            border-left: 6px solid {color}; margin-bottom: 1rem;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                            <span style="font-weight: 600; font-size: 1.1rem;">{company}</span>
                            <span style="background: {color}; color: white; padding: 0.2rem 0.6rem; 
                                  border-radius: 12px; font-size: 0.7rem; margin-left: 0.5rem;">
                                {badge}
                            </span>
                        </div>
                        <div style="font-size: 2rem; font-weight: 700; color: {color};">{score:.0f}%</div>
                    </div>
                    <p style="color: #6b7280; font-size: 0.85rem; margin: 0.3rem 0;">
                        {company_data['description']}
                    </p>
                    <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0;">
                        <span style="background: #e5e7eb; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem;">
                            CGPA: {company_data['cgpa_cutoff']}+
                        </span>
                        <span style="background: #e5e7eb; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem;">
                            Coding: {'✅' if company_data['coding_round'] else '❌'}
                        </span>
                        <span style="background: #e5e7eb; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem;">
                            Aptitude: {'✅' if company_data['aptitude_round'] else '❌'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expander for details
                with st.expander(f"📋 View detailed analysis for {company}"):
                    st.markdown("**✅ What You're Doing Well:**")
                    good_points = [d for d in details[:5] if "✅" in d or "✓" in d]
                    if good_points:
                        for point in good_points[:3]:
                            st.markdown(f"• {point.replace('✅', '').replace('✓', '').strip()}")
                    else:
                        st.markdown("• No strong matches yet")
                    
                    st.markdown("**⚠️ Areas to Improve:**")
                    improve_points = [d for d in details[:5] if "⚠️" in d]
                    if improve_points:
                        for point in improve_points[:3]:
                            st.markdown(f"• {point.replace('⚠️', '').strip()}")
                    else:
                        st.markdown("• You're doing great!")
                    
                    # Missing critical skills
                    st.markdown("**❌ Missing Critical Skills:**")
                    missing = []
                    for skill in company_data['skills']['critical']:
                        if not any(skill.lower() in s.lower() for s in resume_skills):
                            missing.append(skill)
                    
                    if missing:
                        for skill in missing[:5]:
                            st.markdown(f"- {skill}")
                    else:
                        st.success("✅ You have all critical skills!")
        else:
            st.info("No companies in selected category")

def get_company_recommendations(resume_skills, cgpa, experience):
    """Get top 3 company recommendations based on score"""
    
    recommendations = []
    scores = []
    
    for company in COMPANY_REQUIREMENTS.keys():
        score, _ = calculate_company_score(resume_skills, company, cgpa, experience)
        scores.append((company, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    for company, score in scores[:3]:
        recommendations.append({
            "company": company,
            "score": score,
            "icon": COMPANY_REQUIREMENTS[company].get('icon', '🏢')
        })
    
    return recommendations