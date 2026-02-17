# ============================================
# STREAMLIT_APP.PY - Main application entry point
# ============================================

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import os

from constants import INDUSTRY_TEMPLATES, EXPERIENCE_LEVELS, get_sample_jd
from utils import clear_history, init_db, save_scan_history, load_scan_history, check_ml_status_realtime, get_ml_insights, enhance_bullet_point, calculate_optimized_score
from utils import generate_ats_pdf, update_pdf_export_flag, update_company_sim_count, get_user_stats
from utils import delete_scan, delete_multiple_scans, get_scan_by_id
from components import render_sidebar, render_resume_input, render_job_description, display_ml_insights
from components import display_score_tab, display_keyword_tab, display_normalization_tab, display_recommendations_tab
from achievements import display_achievements, check_achievements, calculate_user_level, ACHIEVEMENTS

# Page config
st.set_page_config(
    page_title="Indian ATS Resume Scanner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Modern Theme
st.markdown("""
<style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ===== GLOBAL STYLES ===== */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: #f8fafc;
    }
    
    /* ===== HEADER SECTION ===== */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        padding-top: 1rem;
    }
    
    .sub-header {
        color: #64748b;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 1.5rem;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    .css-1d391kg, .css-163ttbj, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 10px rgba(0,0,0,0.02);
    }
    
    /* Navigation radio buttons */
    .stRadio > div {
        background: white;
        padding: 0.8rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .stRadio label {
        font-weight: 500;
        color: #334155;
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stRadio label:hover {
        background: #f1f5f9;
        color: #1e3c72;
    }
    
    /* ===== MAIN CONTENT CARDS ===== */
    .main-card {
        background: white;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border: 1px solid #e9eef2;
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .main-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #eef2f6;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-header span {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* ===== BUTTON CONTAINER FOR LOAD/CLEAR ===== */
    .button-container {
        display: flex;
        gap: 10px;
        margin-top: 5px;
    }
    
    .button-container .stButton {
        flex: 1;
    }
    
    .button-container .stButton button {
        width: 100%;
        border-radius: 40px;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.4rem 1rem;
    }
    
    /* ===== SCORE CARD ===== */
    .score-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    
    .score-card h1 {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
        color: white;
    }
    
    .score-card p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        background: white;
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3c72;
        margin: 0;
    }
    
    .metric-card p {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.3rem 0 0 0;
    }
    
    /* ===== FEEDBACK BOXES ===== */
    .feedback-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* ===== SKILL CHIPS ===== */
    .skill-chip {
        display: inline-block;
        background: #eef2ff;
        color: #1e3c72;
        padding: 0.4rem 1rem;
        margin: 0.3rem;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 500;
        border: 1px solid #cbd5e1;
        transition: all 0.2s;
    }
    
    .skill-chip:hover {
        background: #1e3c72;
        color: white;
        border-color: #1e3c72;
        transform: translateY(-1px);
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f1f5f9;
        padding: 0.5rem;
        border-radius: 40px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        color: #475569;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1e3c72 !important;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* ===== BUTTONS ===== */
    .stButton button {
        border-radius: 40px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.5rem 2rem;
        transition: all 0.2s;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton button[type="primary"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .stButton button[type="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
    }
    
    .stButton button[type="secondary"] {
        background: white;
        color: #1e3c72;
        border: 1px solid #cbd5e1;
    }
    
    .stButton button[type="secondary"]:hover {
        background: #f8fafc;
        border-color: #94a3b8;
    }
    
    /* ===== INPUT FIELDS ===== */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2a5298;
        box-shadow: 0 0 0 3px rgba(42,82,152,0.1);
    }
    
    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        border-radius: 20px;
    }
    
    /* ===== ATS METER ===== */
    .ats-meter {
        height: 10px;
        background: #e2e8f0;
        border-radius: 20px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .ats-fill {
        height: 100%;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        border-radius: 20px;
        transition: width 0.5s ease;
    }
    
    /* ===== TABLES ===== */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    .dataframe th {
        background: #f8fafc;
        color: #1e293b;
        font-weight: 600;
        padding: 0.8rem !important;
    }
    
    .dataframe td {
        padding: 0.8rem !important;
        border-bottom: 1px solid #eef2f6;
    }
    
    /* ===== STATUS BADGES ===== */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .status-online {
        background: #10b981;
        color: white;
    }
    
    .status-offline {
        background: #ef4444;
        color: white;
    }
    
    /* ===== COMPANY CARDS ===== */
    .company-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
        border-left: 4px solid #2a5298;
    }
    
    .company-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }
    
    /* ===== ML CARDS ===== */
    .ml-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .ml-badge {
        background: #8b5cf6;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    /* ===== ACHIEVEMENT CARDS ===== */
    .achievement-card {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .level-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
    }
    
    /* ===== NORMALIZATION BADGES ===== */
    .normalized-badge {
        background: #10b981;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }
    
    /* ===== DELETE BUTTON ===== */
    .delete-btn {
        color: #ef4444;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .delete-btn:hover {
        color: #dc2626;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem 0 1rem 0;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    
    .footer strong {
        color: #1e293b;
    }
    
    /* ===== BUILDER STYLES ===== */
    .builder-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    
    .step {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        background: #f1f5f9;
        margin: 0 0.3rem;
        border-radius: 30px;
        color: #64748b;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .step.active {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .resume-preview {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-grid {
            grid-template-columns: 1fr 1fr;
        }
        
        .score-card h1 {
            font-size: 3rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
        
        .button-container {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize database and session state
init_db()

# Initialize all session state variables
if 'builder_step' not in st.session_state:
    st.session_state.builder_step = 1
if 'optimized_resume' not in st.session_state:
    st.session_state.optimized_resume = None
if 'builder_jd' not in st.session_state:
    st.session_state.builder_jd = ""
if 'enable_ml' not in st.session_state:
    st.session_state.enable_ml = False
if 'ml_available' not in st.session_state:
    st.session_state.ml_available = False
if 'company_skills' not in st.session_state:
    st.session_state.company_skills = []
if 'company_cgpa' not in st.session_state:
    st.session_state.company_cgpa = 7.5
if 'company_exp' not in st.session_state:
    st.session_state.company_exp = 0
if 'company_sim_count' not in st.session_state:
    st.session_state.company_sim_count = 0
if 'pdf_exported' not in st.session_state:
    st.session_state.pdf_exported = False
if 'show_achievements' not in st.session_state:
    st.session_state.show_achievements = False
if 'selected_scans' not in st.session_state:
    st.session_state.selected_scans = []
if 'show_delete_confirmation' not in st.session_state:
    st.session_state.show_delete_confirmation = False
if 'show_clear_confirmation' not in st.session_state:
    st.session_state.show_clear_confirmation = False

# Header with professional styling
st.markdown('<h1 class="main-header">🇮🇳 Indian ATS Resume Scanner</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Optimize your resume for Indian job portals and ATS systems</p>', unsafe_allow_html=True)

# Render sidebar
app_mode, industry, experience_level = render_sidebar()

# Display achievements in sidebar if enabled
if st.session_state.get('show_achievements', False):
    with st.sidebar:
        st.markdown("---")
        display_achievements()

# ============================================
# SCAN RESUME MODE
# ============================================
if app_mode == "📤 Scan Resume":
    # Main content card
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📄 Resume Scanner <span>PRO</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        option, uploaded_file, resume_text = render_resume_input()
    
    with col2:
        job_title, job_description = render_job_description(industry)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 ANALYZE RESUME WITH ATS", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if analyze_button:
        resume_error = (uploaded_file is None and option == "📤 Upload Resume") and (not resume_text and option == "📝 Paste Text")
        if resume_error:
            st.error("❌ Please upload a resume or paste resume text!")
        elif not job_description:
            st.error("❌ Please enter a job description!")
        else:
            with st.spinner("🔄 Analyzing your resume..."):
                try:
                    API_URL = "http://localhost:8000"
                    
                    if option == "📤 Upload Resume" and uploaded_file:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {
                            "job_description": job_description,
                            "job_title": job_title if job_title else industry.replace("💻 ", "").replace("🏦 ", "").replace("🏭 ", "").replace("🏛️ ", "").replace("📊 ", "").replace("📱 ", "")
                        }
                        response = requests.post(f"{API_URL}/api/scan", files=files, data=data)
                        resume_name = uploaded_file.name
                        text_for_ml = "Resume from file"
                        if response.status_code == 200:
                            results = response.json()
                            st.session_state.company_skills = results.get("parsed_data", {}).get("skills", [])
                    else:
                        data = {
                            "resume_text": resume_text,
                            "job_description": job_description
                        }
                        response = requests.post(f"{API_URL}/api/analyze-text", data=data)
                        resume_name = "Pasted Resume"
                        text_for_ml = resume_text
                        if response.status_code == 200:
                            results = response.json()
                            st.session_state.company_skills = results.get("parsed_data", {}).get("skills", [])
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        save_scan_history(
                            resume_name=resume_name,
                            job_title=job_title if job_title else industry,
                            industry=industry,
                            experience_level=experience_level,
                            ats_score=results["ats_analysis"]["overall_score"],
                            skills_found=len(results["parsed_data"]["skills"]),
                            missing_keywords=results["ats_analysis"].get("missing_keywords", []),
                            recommendations=results.get("recommendations", [])
                        )
                        
                        # Results card
                        st.markdown('<div class="main-card">', unsafe_allow_html=True)
                        st.markdown("## 📊 ATS Analysis Results")
                        
                        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Score", "🔍 Keyword Analysis", "🇮🇳 Indian Normalization", "📈 Recommendations"])
                        
                        with tab1:
                            display_score_tab(results)
                        with tab2:
                            display_keyword_tab(results, industry)
                        with tab3:
                            display_normalization_tab(results)
                        with tab4:
                            display_recommendations_tab(results, industry, experience_level)
                        
                        if st.session_state.enable_ml and st.session_state.ml_available:
                            with st.spinner("🧠 Generating ML insights..."):
                                ml_insights = get_ml_insights(text_for_ml, job_description)
                                if ml_insights:
                                    st.markdown("### 🧠 AI-Powered Insights")
                                    display_ml_insights(ml_insights)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Download card
                        st.markdown('<div class="main-card">', unsafe_allow_html=True)
                        st.markdown("### 📥 Download Your Optimized Resume")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.download_button(
                                label="📦 Download JSON Report",
                                data=json.dumps(results, indent=2),
                                file_name=f"ats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True,
                                help="Download raw analysis data in JSON format"
                            )
                        
                        with col2:
                            try:
                                parsed_data = results.get('parsed_data', {})
                                ats_analysis = results.get('ats_analysis', {})
                                
                                candidate_name = "Your Name"
                                if parsed_data.get('entities', {}).get('PERSON'):
                                    candidate_name = parsed_data['entities']['PERSON'][0]
                                elif resume_name != "Pasted Resume":
                                    candidate_name = resume_name.replace('.pdf', '').replace('.docx', '').replace('_', ' ').title()
                                
                                skills_list = parsed_data.get('skills', [])
                                
                                experience_list = []
                                for exp in parsed_data.get('experience', [])[:2]:
                                    experience_list.append({
                                        'company': exp.get('company', 'Company Name'),
                                        'duration': exp.get('duration', 'Full Time'),
                                        'description': exp.get('description', '- Worked on projects\n- Collaborated with team')
                                    })
                                
                                missing_keywords = ats_analysis.get('missing_keywords', [])
                                
                                pdf_resume_data = {
                                    'name': candidate_name,
                                    'email': parsed_data.get('entities', {}).get('EMAIL', ['email@example.com'])[0] if parsed_data.get('entities', {}).get('EMAIL') else 'email@example.com',
                                    'phone': parsed_data.get('entities', {}).get('PHONE', ['+91 98765 43210'])[0] if parsed_data.get('entities', {}).get('PHONE') else '+91 98765 43210',
                                    'location': parsed_data.get('indian_info', {}).get('locations', ['India'])[0] if parsed_data.get('indian_info', {}).get('locations') else 'India',
                                    'summary': f"ATS Score: {ats_analysis['overall_score']}/100. {ats_analysis['feedback'][0] if ats_analysis.get('feedback') else 'Optimized resume based on job requirements.'}",
                                    'skills': skills_list,
                                    'experience': experience_list,
                                    'education': 'B.Tech in Computer Science - University of Mumbai, 2024\nCGPA: 8.2/10',
                                    'projects': '- Key projects highlighted in resume\n- Additional projects available upon request',
                                    'certifications': ', '.join(missing_keywords[:3]) + ' (Recommended)' if missing_keywords else '- AWS Certified Cloud Practitioner (In Progress)'
                                }
                                
                                pdf_file = generate_ats_pdf(
                                    pdf_resume_data,
                                    ats_analysis['overall_score'],
                                    job_title if job_title else "Software Engineer"
                                )
                                
                                if pdf_file:
                                    with open(pdf_file, 'rb') as f:
                                        st.download_button(
                                            label="📄 Download ATS-Optimized PDF",
                                            data=f,
                                            file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True,
                                            help="Download professionally formatted PDF resume optimized for ATS"
                                        )
                                    os.unlink(pdf_file)
                                    update_pdf_export_flag()
                                else:
                                    st.error("❌ PDF generation failed")
                            except Exception as e:
                                st.error(f"⚠️ PDF generation failed: {str(e)[:50]}...")
                                st.info("💡 Install required library: `pip install fpdf2`")
                        
                        with col3:
                            text_content = f"""
RESUME ANALYSIS REPORT
=======================
File: {resume_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
ATS Score: {ats_analysis['overall_score']}/100

KEY FINDINGS
------------
Skills Found: {len(skills_list)}
Missing Keywords: {len(missing_keywords)}

RECOMMENDATIONS
---------------
{chr(10).join([f'{i+1}. {rec}' for i, rec in enumerate(results.get('recommendations', [])[:5])])}

GENERATED BY INDIAN ATS RESUME SCANNER v3.0
"""
                            st.download_button(
                                label="📝 Download Text Report",
                                data=text_content,
                                file_name=f"ats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True,
                                help="Download analysis report as plain text"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        achievements = check_achievements()
                        if achievements:
                            with st.expander("🏆 Achievements Unlocked!", expanded=True):
                                for ach in achievements[-3:]:
                                    if ach in ACHIEVEMENTS:
                                        a = ACHIEVEMENTS[ach]
                                        st.markdown(f"""
                                        <div class="achievement-card">
                                            <div style="display: flex; align-items: center;">
                                                <span style="font-size: 2rem; margin-right: 1rem;">{a['icon']}</span>
                                                <div>
                                                    <h4 style="color: white; margin:0;">{a['name']}</h4>
                                                    <p style="color: white; opacity: 0.9; margin:0;">{a['description']}</p>
                                                    <p style="color: white; opacity: 0.8; margin:0; font-size: 0.8rem;">+{a['points']} points</p>
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Backend server not running! Start with: python app.py")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================
# BUILD RESUME MODE
# ============================================
elif app_mode == "📝 Build Resume":
    from resume_builder import show_resume_builder
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    show_resume_builder()
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# COMPANY ATS SIMULATOR MODE
# ============================================
elif app_mode == "🏢 Company ATS":
    from company_simulator import show_company_simulator
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                color: white; padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
        <h1 style="color: white; margin:0; font-size: 2rem;">🏢 Company-Specific ATS Simulator</h1>
        <p style="color: rgba(255,255,255,0.9); margin:0.5rem 0 0 0; font-size: 1.1rem;">
            Different companies use different ATS filters. See how you score at TCS, Infosys, Amazon, Google, and more!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Your Skills")
        
        if st.session_state.company_skills:
            st.success(f"✅ Using {len(st.session_state.company_skills)} skills from your last resume scan")
            use_last_scan = st.checkbox("Use these skills", value=True, key="use_last_scan")
            if use_last_scan:
                skills = st.session_state.company_skills
            else:
                skills = []
        else:
            skills = []
        
        if not skills:
            skill_input = st.text_area(
                "Enter your skills (comma-separated)",
                placeholder="Python, Java, SQL, Data Structures, AWS, Communication, Leadership",
                height=150,
                key="company_skill_input"
            )
            if skill_input:
                skills = [s.strip() for s in skill_input.split(',') if s.strip()]
            else:
                skills = ["Python", "SQL", "Data Structures", "Communication"]
                st.info("📌 Using default skills. Enter your own skills above.")
        
        if skills:
            st.markdown("**Your Skills:**")
            skills_html = " ".join([f'<span class="skill-chip">{skill}</span>' for skill in skills[:15]])
            st.markdown(skills_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Your Profile")
        
        cgpa = st.number_input(
            "Your CGPA (out of 10)",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state.company_cgpa,
            step=0.1,
            key="company_cgpa_input"
        )
        st.session_state.company_cgpa = cgpa
        
        experience = st.selectbox(
            "Years of Experience",
            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            index=st.session_state.company_exp,
            key="company_exp_input"
        )
        st.session_state.company_exp = experience
    
    show_company_simulator(skills, cgpa, experience)
    update_company_sim_count()
    
    if st.session_state.company_sim_count == 5:
        st.success("🏆 Achievement Unlocked: Company Explorer! You've simulated 5+ companies.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# HISTORY MODE
# ============================================
elif app_mode == "📊 History":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Resume Scan History")
    
    # Load history with higher limit for full view
    df = load_scan_history(limit=100)
    
    if not df.empty:
        # Get user stats for display
        stats = get_user_stats()
        
        # Metric cards in a grid
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Scans", stats['total_scans'])
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Avg Score", f"{stats['avg_score']:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Best Score", f"{stats['best_score']:.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Max Skills", stats['max_skills'])
            st.markdown('</div>', unsafe_allow_html=True)
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔥 Streak", f"{stats['streak']} days")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ============= DELETE CONTROLS =============
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("✅ Select All", use_container_width=True):
                st.session_state.selected_scans = df['id'].tolist()
                st.rerun()
        
        with col2:
            if st.button("❌ Deselect All", use_container_width=True):
                st.session_state.selected_scans = []
                st.rerun()
        
        with col3:
            if st.session_state.selected_scans:
                delete_count = len(st.session_state.selected_scans)
                if st.button(f"🗑️ Delete Selected ({delete_count})", 
                           type="primary", 
                           use_container_width=True):
                    st.session_state.show_delete_confirmation = True
        
        with col4:
            if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
                st.session_state.show_clear_confirmation = True
        
        # Delete Confirmation Dialog
        if st.session_state.get('show_delete_confirmation', False):
            st.warning(f"⚠️ Are you sure you want to delete {len(st.session_state.selected_scans)} scan(s)? This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", use_container_width=True):
                    delete_multiple_scans(st.session_state.selected_scans)
                    st.session_state.selected_scans = []
                    st.session_state.show_delete_confirmation = False
                    st.success(f"✅ Deleted {delete_count} scan(s)!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
        
        # Clear All Confirmation Dialog
        if st.session_state.get('show_clear_confirmation', False):
            st.error("⚠️ **WARNING:** This will delete ALL your scan history permanently!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Clear All", use_container_width=True):
                    clear_history()
                    st.session_state.selected_scans = []
                    st.session_state.show_clear_confirmation = False
                    st.success("✅ All history cleared!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_clear_confirmation = False
                    st.rerun()
        
        st.markdown("---")
        
        # ============= SCORE TREND CHARTS =============
        tab1, tab2 = st.tabs(["📈 Score Trend", "📊 Skills Trend"])
        
        with tab1:
            fig = px.line(df, x='date', y='ats_score', 
                         title='ATS Score Trend Over Time', 
                         markers=True, 
                         color_discrete_sequence=['#1e3c72'])
            fig.update_layout(height=400, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if len(df) > 1:
                fig2 = px.line(df, x='date', y='skills_found',
                              title='Skills Detected Over Time',
                              markers=True,
                              color_discrete_sequence=['#10b981'])
                fig2.update_layout(height=300, plot_bgcolor='white')
                st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # ============= DETAILED SCAN HISTORY TABLE =============
        st.markdown("### 📋 Detailed Scan History")
        
        # Prepare display dataframe
        display_df = df.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
        display_df['select'] = display_df['id'].apply(
            lambda x: x in st.session_state.selected_scans
        )
        
        # Keep ID in the dataframe but don't display it
        column_order = ['select', 'date', 'resume_name', 'job_title', 'industry', 
                       'ats_score', 'skills_found', 'missing_keywords']
        
        # Display as editable dataframe with checkboxes
        edited_df = st.data_editor(
            display_df[column_order],
            use_container_width=True,
            hide_index=True,
            column_config={
                "select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select scans to delete",
                    default=False,
                    width="small"
                ),
                "date": st.column_config.DatetimeColumn(
                    "Date",
                    format="YYYY-MM-DD HH:mm",
                    width="medium"
                ),
                "resume_name": "Resume",
                "job_title": "Job Title",
                "industry": "Industry",
                "ats_score": st.column_config.NumberColumn(
                    "ATS Score",
                    format="%.0f",
                    width="small"
                ),
                "skills_found": st.column_config.NumberColumn(
                    "Skills",
                    width="small"
                ),
                "missing_keywords": st.column_config.TextColumn(
                    "Missing Keywords",
                    width="large"
                )
            },
            disabled=['date', 'resume_name', 'job_title', 'industry', 
                     'ats_score', 'skills_found', 'missing_keywords'],
            key="history_editor"
        )
        
        # Update selection based on checkbox changes
        if edited_df is not None and 'select' in edited_df.columns:
            selected_indices = edited_df[edited_df['select'] == True].index
            selected_ids = df.iloc[selected_indices]['id'].tolist()
            st.session_state.selected_scans = selected_ids
        
        # ============= INDIVIDUAL DELETE BUTTONS =============
        with st.expander("🗑️ Delete Individual Scans"):
            st.markdown("Click the trash icon to delete a specific scan:")
            
            for idx, row in df.head(10).iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.5, 1, 1, 0.5])
                with col1:
                    st.write(f"**{row['date'][:10]}**")
                with col2:
                    st.write(f"{row['resume_name'][:20]}..." if len(row['resume_name']) > 20 else row['resume_name'])
                with col3:
                    st.write(f"{row['job_title'][:15]}..." if len(row['job_title']) > 15 else row['job_title'])
                with col4:
                    st.write(f"Score: {row['ats_score']:.0f}")
                with col5:
                    st.write(f"Skills: {row['skills_found']}")
                with col6:
                    if st.button(f"🗑️", key=f"delete_{row['id']}", help="Delete this scan"):
                        delete_scan(row['id'])
                        st.success(f"✅ Deleted scan from {row['date'][:10]}")
                        st.rerun()
        
        # ============= EXPORT OPTIONS =============
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export All as CSV",
                data=csv,
                file_name=f"scan_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            if st.button("🏆 View My Achievements", use_container_width=True):
                st.session_state.show_achievements = not st.session_state.show_achievements
                st.rerun()
        
        with col3:
            if st.button("🔄 Refresh History", use_container_width=True):
                st.rerun()
    
    else:
        st.info("📭 No scan history yet. Analyze your first resume to see history here!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Go to Scan Resume", use_container_width=True):
                st.session_state.app_mode = "📤 Scan Resume"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ACHIEVEMENTS PAGE (when toggled)
# ============================================
if st.session_state.get('show_achievements', False) and app_mode != "📊 History":
    with st.expander("🏆 Your Achievements & Progress", expanded=True):
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        display_achievements()
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("""
<p>🇮🇳 <strong>Indian ATS Resume Scanner v3.0</strong> • Built for Indian job seekers</p>
<p>📄 PDF Export • 🧠 ML Insights • 🎯 ATS Scoring • 🇮🇳 Indian Normalization • 🏢 Company ATS • 🏆 Achievements • 🗑️ History Management</p>
<p style="font-size: 0.8rem;">Optimize for Naukri, Indeed, LinkedIn India • TCS • Infosys • Wipro • Amazon • Google • Microsoft</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)