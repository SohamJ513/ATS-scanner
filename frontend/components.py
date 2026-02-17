# ============================================
# COMPONENTS.PY - All reusable UI components
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from constants import INDUSTRY_TEMPLATES, EXPERIENCE_LEVELS
from utils import check_ml_status_realtime, load_scan_history, clear_history, delete_scan, get_user_stats

# ============= SIDEBAR COMPONENTS =============
def render_sidebar():
    """Render the complete sidebar"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.title("Navigation")
        
        # Navigation options
        app_mode = st.radio(
            "Choose Mode:",
            ["📤 Scan Resume", "📝 Build Resume", "🏢 Company ATS", "📊 History"],
            key="app_mode"
        )
        
        st.markdown("---")
        render_ml_status()
        st.markdown("---")
        
        industry = "All Industries"
        experience_level = "All Levels"
        
        if app_mode == "📤 Scan Resume":
            st.markdown("### 🏢 Industry Focus")
            industry = st.selectbox(
                "Select your industry:",
                options=list(INDUSTRY_TEMPLATES.keys()),
                index=0,
                key="scan_industry"
            )
            
            st.markdown("### 📈 Experience Level")
            experience_level = st.selectbox(
                "Select your experience:",
                options=list(EXPERIENCE_LEVELS.keys()),
                index=0,
                key="scan_exp"
            )
        
        st.markdown("---")
        
        # Show history sidebar only in History mode
        if app_mode == "📊 History":
            render_history_sidebar()
        
        # Show tips for Company ATS mode
        if app_mode == "🏢 Company ATS":
            render_company_tips()
        
        render_tips_section()
        render_about_section()
        
        return app_mode, industry, experience_level

def render_ml_status():
    """Render ML status section in sidebar"""
    st.markdown("### 🤖 ML Status")
    ml_status = check_ml_status_realtime()
    st.session_state.ml_available = ml_status.get("available", False)
    st.session_state.ml_status_details = ml_status.get("full_response", {})
    
    if st.session_state.ml_available:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <span style="color: #10b981; font-weight: 600;">✅ ML Engine Online</span>
            <span class="status-badge status-online">v{ml_status.get('version', '1.0')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🧪 Experimental Features")
        enable_ml = st.checkbox(
            "Enable ML-Powered Insights",
            value=st.session_state.get('enable_ml', False),
            help="Use AI to understand resume meaning, not just keywords"
        )
        st.session_state.enable_ml = enable_ml
        
        if enable_ml:
            st.success("✅ ML insights enabled")
            st.caption("• Semantic matching\n• Smart skill detection\n• Key phrase extraction")
            if ml_status.get("model_ready"):
                st.info("📦 Model: Ready")
            else:
                st.warning("📦 Model: Will download on first use (~80MB)")
    else:
        st.markdown("""
        <div style="display: flex; align-items: center;">
            <span style="color: #ef4444; font-weight: 600;">❌ ML Engine Offline</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📥 Setup Instructions", expanded=True):
            st.markdown("""
            1. **Start backend server:**
            ```bash
            cd backend
            python app.py
            ```
            2. **Refresh this page**
            """)
            if st.button("🔄 Test Connection Now"):
                test_status = check_ml_status_realtime()
                if test_status.get("available"):
                    st.success("✅ Backend is now available! Refresh the page.")
                    st.rerun()
                else:
                    st.error("❌ Cannot connect. Make sure backend is running.")

def render_history_sidebar():
    """Render enhanced history section in sidebar with delete functionality"""
    st.markdown("### 📊 Scan History")
    
    df = load_scan_history(limit=5)
    stats = get_user_stats()
    
    if not df.empty:
        # Show streak and total scans in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔥 Streak", f"{stats['streak']} days")
        with col2:
            st.metric("📊 Total", stats['total_scans'])
        
        # Mini trend chart
        if len(df) > 1:
            fig = px.line(df, x='date', y='ats_score', 
                         title='Score Trend',
                         markers=True,
                         height=150,
                         color_discrete_sequence=['#667eea'])
            fig.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
                xaxis_title="",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent scans with delete buttons
        st.markdown("**Recent Scans:**")
        for _, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 0.5])
            with col1:
                st.markdown(f"📄 {row['date'][5:10]}")
            with col2:
                st.markdown(f"**{row['ats_score']:.0f}**")
            with col3:
                st.markdown(f"⚡{row['skills_found']}")
            with col4:
                if st.button("🗑️", key=f"side_del_{row['id']}", help="Delete this scan"):
                    delete_scan(row['id'])
                    st.rerun()
        
        # Clear all button with confirmation
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.show_sidebar_clear_confirmation = True
        
        if st.session_state.get('show_sidebar_clear_confirmation', False):
            st.warning("⚠️ Delete all history?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes", key="sidebar_clear_yes"):
                    clear_history()
                    st.session_state.show_sidebar_clear_confirmation = False
                    st.rerun()
            with col2:
                if st.button("❌ No", key="sidebar_clear_no"):
                    st.session_state.show_sidebar_clear_confirmation = False
                    st.rerun()
    else:
        st.info("📭 No scans yet")
        st.markdown("*Analyze your first resume to start tracking!*")

def render_company_tips():
    """Render tips for Company ATS mode"""
    st.markdown("### 🏢 Company ATS Tips")
    
    # Create expandable sections for each company tier
    with st.expander("🥇 Top Tier Companies", expanded=False):
        st.markdown("""
        **Amazon** 📦
        • Leadership Principles
        • System Design
        • DSA optimization
        
        **Google** 🔍
        • Advanced Algorithms
        • Problem Solving
        • OS & Networking
        
        **Microsoft** 🪟
        • C#/.NET
        • Azure Cloud
        • Design Patterns
        """)
    
    with st.expander("🥈 Mid Tier Companies", expanded=False):
        st.markdown("""
        **TCS Digital** 💎
        • Advanced DSA
        • System Design
        • Cloud Computing
        
        **Infosys PP** ⚡
        • Competitive Programming
        • Multiple Languages
        • Hackathon Wins
        
        **Wipro Turbo** 🚀
        • Microservices
        • DevOps
        • Cloud Basics
        """)
    
    with st.expander("🎓 Fresher Friendly", expanded=False):
        st.markdown("""
        **TCS Ninja** 🔵
        • Core Java/Python
        • SQL & DBMS
        • Aptitude
        
        **Accenture** 🟣
        • Communication
        • Any Programming
        • Agile Basics
        
        **Cognizant** 🟢
        • Java/.NET
        • Testing
        • Web Technologies
        """)

def render_tips_section():
    """Render tips section"""
    with st.expander("📋 Tips for Indian Job Seekers", expanded=False):
        st.markdown("""
        ### 📄 Resume Tips
        1. **Use standard section headers** (Experience, Education, Skills)
        2. **Include Indian degree names** (B.Tech, MCA, B.Sc, etc.)
        3. **Add location preferences** (Bangalore, Mumbai, Pune, etc.)
        4. **List Indian companies** with proper names
        5. **Include Indian certifications** (NPTEL, IIT courses)
        
        ### ⚡ Quick Wins
        • **Quantify achievements** with numbers and percentages
        • **Use action verbs** (Developed, Led, Implemented)
        • **Save as PDF** for best ATS compatibility
        • **Avoid tables, images, and columns**
        """)

def render_about_section():
    """Render about section"""
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        ### 🇮🇳 Indian ATS Resume Scanner v2.2
        
        Built specifically for the Indian job market by developers who understand local hiring challenges.
        
        **✨ Features:**
        • 🎯 **ATS Score Calculator** - 0-100 scoring
        • 🇮🇳 **Indian Normalization** - Degrees, Companies, Cities
        • 🧠 **ML-Powered Insights** - Semantic matching
        • 📝 **Resume Builder** - ATS-optimized templates
        • 🏢 **Company Simulator** - TCS, Infosys, Amazon, Google
        • 📊 **History Tracking** - Progress & achievements
        • 📄 **PDF Export** - Professional formatting
        • 🏆 **Gamification** - Levels & achievements
        
        **🏢 Supported Companies:**
        `TCS` • `Infosys` • `Wipro` • `Amazon` • `Google` • `Microsoft` • `Accenture` • `Cognizant`
        
        ---
        **📌 Note:** This tool provides recommendations. Always review your resume manually before submitting.
        
        *Made with ❤️ for Indian job seekers*
        """)

# ============= RESUME INPUT COMPONENTS =============
def render_resume_input():
    """Render resume input section"""
    st.markdown('<h3 class="sub-header">📄 Resume Input</h3>', unsafe_allow_html=True)
    
    option = st.radio(
        "Choose Input Method:",
        ["📤 Upload Resume", "📝 Paste Text"],
        key="scan_option",
        horizontal=True
    )
    
    uploaded_file = None
    resume_text = ""
    
    if option == "📤 Upload Resume":
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)", 
            type=['pdf', 'docx'],
            help="Supported formats: PDF, DOCX. Max size: 10MB",
            accept_multiple_files=False
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            if file_size < 10240:  # 10MB
                st.success(f"✅ Uploaded: {uploaded_file.name} ({file_size:.0f} KB)")
            else:
                st.error("❌ File too large. Max size: 10MB")
                uploaded_file = None
    else:
        resume_text = st.text_area(
            "Paste your resume text:",
            height=350,
            placeholder="Paste your resume content here...\n\nInclude:\n• Education\n• Work Experience\n• Skills\n• Projects\n• Certifications",
            help="Include education, experience, skills, and projects for best results"
        )
    
    return option, uploaded_file, resume_text

def render_job_description(industry):
    """Render job description input section"""
    from constants import get_sample_jd
    
    st.markdown('<h3 class="sub-header">🎯 Job Description</h3>', unsafe_allow_html=True)
    
    job_title = st.text_input(
        "Job Title (Optional):", 
        placeholder="e.g., Python Developer, Data Analyst, Software Engineer",
        help="Enter the job title you're targeting"
    )
    
    job_description = st.text_area(
        "Paste Job Description:",
        height=250,
        placeholder="Paste the complete job description here...",
        help="Include required skills, qualifications, experience, and responsibilities"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📋 Load {industry} Sample", use_container_width=True):
            job_description = get_sample_jd(industry)
    
    with col2:
        if st.button("🧹 Clear", use_container_width=True):
            job_description = ""
    
    return job_title, job_description

# ============= RESULTS DISPLAY COMPONENTS =============
def display_ml_insights(ml_insights):
    """Display ML insights in a nice format"""
    if not ml_insights:
        return
    
    st.markdown("---")
    st.markdown("### 🧠 ML-Powered Insights (Experimental)")
    st.markdown('<span class="ml-badge">BETA</span>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        semantic_score = ml_insights.get("semantic_analysis", {}).get("semantic_similarity", 0)
        interpretation = ml_insights.get("semantic_analysis", {}).get("interpretation", "")
        
        # Color based on score
        if semantic_score >= 80:
            bg_color = "#10b981"
        elif semantic_score >= 60:
            bg_color = "#f59e0b"
        else:
            bg_color = "#6b7280"
        
        st.markdown(f"""
        <div style="background: {bg_color}; color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <h4 style="color: white; margin-bottom: 0.5rem;">📊 Semantic Match</h4>
            <h2 style="color: white; font-size: 2.5rem;">{semantic_score:.0f}%</h2>
            <p style="color: rgba(255,255,255,0.9);">{interpretation}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        skill_gaps = ml_insights.get("skill_intelligence", {}).get("skill_gaps", [])
        gap_count = len(skill_gaps)
        
        # Color based on gap count
        if gap_count <= 2:
            bg_color = "#10b981"
        elif gap_count <= 5:
            bg_color = "#f59e0b"
        else:
            bg_color = "#ef4444"
        
        st.markdown(f"""
        <div style="background: {bg_color}; color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <h4 style="color: white; margin-bottom: 0.5rem;">🎯 Smart Skill Gaps</h4>
            <h2 style="color: white; font-size: 2.5rem;">{gap_count}</h2>
            <p style="color: rgba(255,255,255,0.9);">ML-detected missing skills</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Key phrases
    key_phrases = ml_insights.get("semantic_analysis", {}).get("key_phrases", [])
    if key_phrases:
        with st.expander("📌 Key Phrases Detected by ML"):
            cols = st.columns(2)
            for i, phrase in enumerate(key_phrases[:6]):
                with cols[i % 2]:
                    st.markdown(f"• *{phrase}*")
    
    # Skill suggestions
    suggested_skills = ml_insights.get("skill_intelligence", {}).get("suggested_skills", [])
    if suggested_skills:
        st.markdown("#### 💡 ML-Recommended Skills")
        skills_html = " ".join([
            f'<span style="background-color: #8b5cf6; color: white; padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; display: inline-block; font-size: 0.9rem;">{skill}</span>' 
            for skill in suggested_skills[:8]
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
    
    st.caption("✨ ML insights are experimental and work alongside your ATS score")

def display_score_tab(results):
    """Display score card and feedback"""
    ats_score = results["ats_analysis"]["overall_score"]
    
    # Score color based on value
    if ats_score >= 80:
        score_color = "#10b981"
        score_message = "🎉 Excellent!"
    elif ats_score >= 60:
        score_color = "#f59e0b"
        score_message = "📈 Good"
    else:
        score_color = "#ef4444"
        score_message = "🔧 Needs Work"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {score_color} 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h1 style="font-size: 3rem; margin: 0;">{ats_score:.0f}</h1>
            <p style="font-size: 1.2rem; margin: 0;">ATS Score</p>
            <p style="opacity: 0.9; margin: 0;">out of 100</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"**{score_message}**")
        
        if ats_score >= 80:
            st.markdown("Your resume is highly ATS-optimized")
        elif ats_score >= 60:
            st.markdown("Minor improvements will boost your score")
        else:
            st.markdown("Significant improvements needed")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        skills_found = len(results["parsed_data"]["skills"])
        missing_count = len(results["ats_analysis"].get("missing_keywords", []))
        
        st.metric("✅ Skills Found", skills_found)
        st.metric("❌ Keywords Missing", missing_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ATS Meter
    st.markdown("### 📊 ATS Compatibility Meter")
    
    # Determine meter color
    if ats_score >= 80:
        meter_color = "#10b981"
    elif ats_score >= 60:
        meter_color = "#f59e0b"
    else:
        meter_color = "#ef4444"
    
    st.markdown(f"""
    <div style="background: #e5e7eb; height: 10px; border-radius: 5px; margin: 1rem 0;">
        <div style="background: {meter_color}; width: {ats_score}%; height: 10px; border-radius: 5px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed Feedback
    st.markdown("### 📝 Detailed Feedback")
    for feedback in results["ats_analysis"]["feedback"]:
        st.markdown(f'<div class="feedback-box">{feedback}</div>', unsafe_allow_html=True)

def display_keyword_tab(results, industry):
    """Display keyword gap analysis"""
    from constants import INDUSTRY_TEMPLATES
    
    st.markdown("### 🔍 Keyword Gap Analysis")
    
    missing_keywords = results["ats_analysis"].get("missing_keywords", [])
    skills = results["parsed_data"]["skills"]
    
    if missing_keywords:
        # Prepare data for visualization
        keyword_data = []
        for kw in missing_keywords[:8]:
            keyword_data.append({"Keyword": kw, "Status": "Missing", "Count": 1})
        for skill in skills[:8]:
            keyword_data.append({"Keyword": skill, "Status": "Found", "Count": 1})
        
        df_keywords = pd.DataFrame(keyword_data)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        found_df = df_keywords[df_keywords["Status"] == "Found"]
        if not found_df.empty:
            fig.add_trace(go.Bar(
                y=found_df["Keyword"],
                x=[100] * len(found_df),
                name="✅ Found",
                orientation='h',
                marker=dict(color='#10b981'),
                text="Found",
                textposition='auto'
            ))
        
        missing_df = df_keywords[df_keywords["Status"] == "Missing"]
        if not missing_df.empty:
            fig.add_trace(go.Bar(
                y=missing_df["Keyword"],
                x=[100] * len(missing_df),
                name="❌ Missing",
                orientation='h',
                marker=dict(color='#ef4444', pattern_shape="/"),
                text="Missing",
                textposition='auto'
            ))
        
        fig.update_layout(
            title="Keyword Match Analysis",
            xaxis_title="Match Status",
            yaxis_title="Keywords",
            barmode='group',
            height=400,
            showlegend=True,
            plot_bgcolor='white',
            hovermode='y'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display missing keywords with priority
        st.markdown("#### ❌ Priority Keywords to Add")
        cols = st.columns(2)
        for i, kw in enumerate(missing_keywords[:6]):
            with cols[i % 2]:
                st.markdown(f"- **{kw}**")
    else:
        st.success("✅ Great! You have all the key keywords from the job description!")
    
    # Skills display
    st.markdown("### 💡 Skills Detected")
    if skills:
        skills_html = " ".join([
            f'<span style="background-color: #dbeafe; color: #1e40af; padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; display: inline-block; font-size: 0.9rem; font-weight: 500;">{skill}</span>' 
            for skill in skills[:20]
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
        
        # Industry benchmark
        if industry != "All Industries":
            st.markdown("#### 🎯 Industry Benchmark")
            industry_skills = INDUSTRY_TEMPLATES[industry]["skills"]
            missing_industry_skills = [s for s in industry_skills if s not in skills]
            
            if missing_industry_skills:
                st.info(f"💡 Top skills in {industry}: {', '.join(missing_industry_skills[:5])}")
    else:
        st.info("⚠️ No specific skills detected. Add technical skills to your resume!")

def display_normalization_tab(results):
    """Display Indian normalization results"""
    st.markdown("### 🇮🇳 Indian-Specific Normalization")
    
    indian_info = results["parsed_data"].get("indian_info", {})
    if indian_info and any(indian_info.get("normalized", {}).values()):
        
        # Degrees
        if indian_info.get("normalized", {}).get("degrees"):
            st.markdown("#### 📚 Standardized Degree Names")
            for i, degree in enumerate(indian_info["degrees"][:5]):
                normalized = indian_info["normalized"]["degrees"][i] if i < len(indian_info["normalized"]["degrees"]) else degree
                if degree != normalized:
                    st.markdown(f"- ~~{degree}~~ → **{normalized}** <span class='normalized-badge'>✓ Standardized</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"- ✅ {degree}")
        
        # Companies
        if indian_info.get("normalized", {}).get("companies"):
            st.markdown("#### 🏢 Standardized Company Names")
            for i, company in enumerate(indian_info["companies"][:5]):
                normalized = indian_info["normalized"]["companies"][i] if i < len(indian_info["normalized"]["companies"]) else company
                if company != normalized:
                    st.markdown(f"- ~~{company}~~ → **{normalized}** <span class='normalized-badge'>✓ Standardized</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"- ✅ {company}")
        
        # Locations
        if indian_info.get("normalized", {}).get("locations"):
            st.markdown("#### 📍 Standardized Locations")
            for i, location in enumerate(indian_info["locations"][:5]):
                normalized = indian_info["normalized"]["locations"][i] if i < len(indian_info["normalized"]["locations"]) else location
                if location != normalized:
                    st.markdown(f"- ~~{location}~~ → **{normalized}** <span class='normalized-badge'>✓ Standardized</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"- ✅ {location}")
    else:
        st.info("📝 No Indian-specific information detected. Add education, companies, or locations to your resume for normalization.")

def display_recommendations_tab(results, industry, experience_level):
    """Display recommendations"""
    from constants import INDUSTRY_TEMPLATES, EXPERIENCE_LEVELS
    
    st.markdown("### 🚀 Actionable Recommendations")
    
    # General recommendations from scanner
    recommendations = results.get("recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    # Industry-specific recommendations
    if industry != "All Industries":
        with st.expander(f"🎯 {industry} Specific Tips", expanded=False):
            industry_tips = [
                f"**Skills to add:** {', '.join(INDUSTRY_TEMPLATES[industry]['skills'][:5])}",
                f"**Degrees to highlight:** {', '.join(INDUSTRY_TEMPLATES[industry]['degrees'][:3])}",
                f"**Keywords to include:** {', '.join(INDUSTRY_TEMPLATES[industry].get('keywords', ['experience', 'projects'])[:3])}"
            ]
            for tip in industry_tips:
                st.markdown(f"- {tip}")
    
    # Experience level recommendations
    if experience_level != "All Levels":
        exp_years = EXPERIENCE_LEVELS[experience_level]
        with st.expander(f"📈 {experience_level} Tips", expanded=False):
            if exp_years <= 1:
                st.markdown("- **Highlight internships** and academic projects")
                st.markdown("- **Include relevant coursework** and certifications")
                st.markdown("- **Add CGPA/percentage** if above 7.5")
                st.markdown("- **Mention hackathons** and coding competitions")
            elif exp_years <= 3:
                st.markdown("- **Quantify achievements** with metrics (%, ₹, time)")
                st.markdown("- **Focus on technologies** and tools used")
                st.markdown("- **Include professional certifications**")
                st.markdown("- **Show impact** of your work")
            elif exp_years <= 6:
                st.markdown("- **Emphasize project leadership** and ownership")
                st.markdown("- **Include team size** and project scale")
                st.markdown("- **Add architecture** and design decisions")
                st.markdown("- **Mention mentoring** junior developers")
            else:
                st.markdown("- **Highlight strategic initiatives** and business impact")
                st.markdown("- **Include mentoring** and team leadership")
                st.markdown("- **Focus on outcomes** and ROI")
                st.markdown("- **Show thought leadership** (blogs, talks, patents)")

