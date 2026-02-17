# ============================================
# UTILS.PY - Database, ML, PDF, and utility functions
# ============================================

import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import streamlit as st
import os
import tempfile

# ============= PDF LIBRARY CHECK =============
# Try to import FPDF, provide helpful error if not installed
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    FPDF = None
    PDF_AVAILABLE = False
    print("⚠️ fpdf2 not installed. PDF export disabled. Run: pip install fpdf2")

# ============= DATABASE FUNCTIONS =============
def init_db():
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  resume_name TEXT,
                  job_title TEXT,
                  industry TEXT,
                  experience_level TEXT,
                  ats_score REAL,
                  skills_found INTEGER,
                  missing_keywords TEXT,
                  recommendations TEXT)''')
    conn.commit()
    conn.close()

def save_scan_history(resume_name, job_title, industry, experience_level, ats_score, skills_found, missing_keywords, recommendations):
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    c.execute("""INSERT INTO scans 
                 (date, resume_name, job_title, industry, experience_level, ats_score, skills_found, missing_keywords, recommendations) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (datetime.now().strftime("%Y-%m-%d %H:%M"), 
               resume_name, 
               job_title if job_title else "General",
               industry,
               experience_level,
               ats_score, 
               skills_found, 
               ', '.join(missing_keywords[:5]), 
               ', '.join(recommendations[:3])))
    conn.commit()
    conn.close()

def load_scan_history(limit=20):
    conn = sqlite3.connect('resume_history.db')
    df = pd.read_sql_query(f"SELECT * FROM scans ORDER BY date DESC LIMIT {limit}", conn)
    conn.close()
    return df

def clear_history():
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM scans")
    conn.commit()
    conn.close()

# ============= DELETE SCAN HISTORY FUNCTIONS =============
def delete_scan(scan_id):
    """Delete a specific scan from history by ID"""
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()

def delete_multiple_scans(scan_ids):
    """Delete multiple scans from history"""
    if not scan_ids:
        return
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(scan_ids))
    c.execute(f"DELETE FROM scans WHERE id IN ({placeholders})", scan_ids)
    conn.commit()
    conn.close()

def get_scan_by_id(scan_id):
    """Get a specific scan by ID"""
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        columns = ['id', 'date', 'resume_name', 'job_title', 'industry', 
                  'experience_level', 'ats_score', 'skills_found', 
                  'missing_keywords', 'recommendations']
        return dict(zip(columns, row))
    return None

# ============= USER STATS FOR ACHIEVEMENTS =============
def get_user_stats():
    """Get user statistics for achievements"""
    conn = sqlite3.connect('resume_history.db')
    c = conn.cursor()
    
    # Total scans
    c.execute("SELECT COUNT(*) FROM scans")
    total_scans = c.fetchone()[0]
    
    # Average score
    c.execute("SELECT AVG(ats_score) FROM scans")
    avg_score = c.fetchone()[0] or 0
    
    # Best score
    c.execute("SELECT MAX(ats_score) FROM scans")
    best_score = c.fetchone()[0] or 0
    
    # Skills stats
    c.execute("SELECT MAX(skills_found) FROM scans")
    max_skills = c.fetchone()[0] or 0
    
    # Scan dates for streak
    c.execute("SELECT date FROM scans ORDER BY date DESC")
    dates = [row[0].split()[0] for row in c.fetchall()]
    
    conn.close()
    
    # Calculate streak
    streak = 0
    if dates:
        today = datetime.now().date()
        current = today
        for date_str in dates:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date == current:
                streak += 1
                current = current - timedelta(days=1)
            else:
                break
    
    return {
        "total_scans": total_scans,
        "avg_score": round(avg_score, 1) if avg_score else 0,
        "best_score": best_score,
        "max_skills": max_skills,
        "streak": streak,
        "unique_days": len(set(dates)) if dates else 0
    }

def update_pdf_export_flag():
    """Set flag when PDF is exported for achievement"""
    st.session_state.pdf_exported = True

def update_company_sim_count():
    """Increment company simulator count for achievement"""
    if 'company_sim_count' not in st.session_state:
        st.session_state.company_sim_count = 0
    st.session_state.company_sim_count += 1

# ============= ML STATUS FUNCTIONS =============
def check_ml_status_realtime():
    """Force real-time check of ML status from backend"""
    try:
        response = requests.get("http://localhost:8000/api/ml/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                "available": data.get("ml_available", False),
                "scanner_ready": data.get("ml_scanner_ready", False),
                "model_ready": data.get("embedding_model_ready", False),
                "version": data.get("ml_version", "unknown"),
                "full_response": data
            }
    except:
        return {"available": False, "error": "Connection refused"}
    return {"available": False}

def get_ml_insights(resume_text, job_description):
    """Fetch ML-powered insights from backend"""
    if not st.session_state.get('enable_ml', False) or not st.session_state.get('ml_available', False):
        return None
    
    try:
        data = {
            "resume_text": resume_text[:3000],
            "job_description": job_description[:3000]
        }
        response = requests.post(
            "http://localhost:8000/api/ml/analyze",
            data=data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("ml_insights")
    except:
        pass
    return None

# ============= TEXT UTILITIES =============
def enhance_bullet_point(text):
    """Enhance bullet points with strong action verbs"""
    from constants import ACTION_VERBS
    text = text.strip('•-* ').strip()
    words = text.split()
    if words:
        first_word = words[0].lower()
        for old, new in ACTION_VERBS.items():
            if first_word.startswith(old):
                words[0] = new
                break
    return ' '.join(words)

def calculate_optimized_score(resume, jd_text):
    """Calculate ATS score for optimized resume"""
    base_score = 75
    keyword_bonus = min(len(resume['keyword_match']) * 2, 15)
    format_bonus = 10
    skill_bonus = min(len(resume.get('suggested_skills', [])) * 1, 5)
    total = base_score + keyword_bonus + format_bonus + skill_bonus
    return min(total, 98)

# ============= PDF EXPORT FUNCTION - ASCII VERSION (NO EMOJIS) =============
def generate_ats_pdf(resume_data, ats_score, job_title):
    """Generate ATS-optimized PDF resume - ASCII only, no emojis"""
    
    # Check if PDF library is available
    if not PDF_AVAILABLE or FPDF is None:
        st.error("📄 PDF generation requires fpdf2. Please install: `pip install fpdf2`")
        return None
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(37, 99, 235)
            self.cell(0, 10, 'ATS-Optimized Resume', 0, 1, 'C')
            self.ln(10)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Generated by Indian ATS Scanner - Page {self.page_no()}', 0, 0, 'C')
    
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Name - remove any special characters
        name = resume_data.get('name', 'Your Name')
        name = ''.join(c for c in name if ord(c) < 128)
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, name, 0, 1, 'L')
        
        # Contact - NO EMOJIS, use plain text
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(75, 85, 99)
        email = resume_data.get('email', 'email@example.com')
        phone = resume_data.get('phone', '+91 98765 43210')
        pdf.cell(0, 6, f"Email: {email} | Phone: {phone}", 0, 1, 'L')
        
        # Location - NO EMOJI
        if resume_data.get('location'):
            location = resume_data.get('location', 'India')
            location = ''.join(c for c in location if ord(c) < 128)
            pdf.cell(0, 6, f"Location: {location}", 0, 1, 'L')
        
        pdf.ln(5)
        
        # ATS Score Badge - NO EMOJI
        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(50, 8, f'ATS Score: {ats_score}/100', 0, 1, 'L', 1)
        pdf.ln(5)
        
        # Professional Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, 'PROFESSIONAL SUMMARY', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        summary = resume_data.get('summary', 'Experienced professional seeking opportunities...')
        summary = ''.join(c for c in summary if ord(c) < 128)
        pdf.multi_cell(0, 6, summary)
        pdf.ln(5)
        
        # Technical Skills - USE HYPHENS INSTEAD OF BULLETS
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, 'TECHNICAL SKILLS', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        skills = resume_data.get('skills', [])
        if skills:
            # Use commas instead of bullets
            skills_text = ', '.join(skills[:15])
            pdf.multi_cell(0, 6, skills_text)
        else:
            pdf.multi_cell(0, 6, 'No skills listed')
        pdf.ln(5)
        
        # Work Experience - USE HYPHENS
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, 'WORK EXPERIENCE', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        experience = resume_data.get('experience', [])
        if experience:
            for exp in experience[:2]:
                pdf.set_font('Arial', 'B', 12)
                company = exp.get('company', 'Company Name')
                company = ''.join(c for c in company if ord(c) < 128)
                pdf.cell(0, 6, company, 0, 1, 'L')
                pdf.set_font('Arial', '', 11)
                pdf.set_text_color(75, 85, 99)
                pdf.cell(0, 5, exp.get('duration', 'Full Time'), 0, 1, 'L')
                pdf.set_text_color(0, 0, 0)
                
                # Replace bullets with hyphens
                description = exp.get('description', '- Worked on projects\n- Collaborated with team')
                description = description.replace('•', '-').replace('●', '-').replace('▶', '-')
                description = ''.join(c for c in description if ord(c) < 128)
                pdf.multi_cell(0, 5, description)
                pdf.ln(3)
        else:
            pdf.multi_cell(0, 6, '- Fresher with strong academic background\n- Completed internships and projects')
        pdf.ln(5)
        
        # Education
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, 'EDUCATION', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        education = resume_data.get('education', 'B.Tech in Computer Science - University of Mumbai, 2024\nCGPA: 8.2/10')
        education = ''.join(c for c in education if ord(c) < 128)
        pdf.multi_cell(0, 6, education)
        pdf.ln(5)
        
        # Projects - USE HYPHENS
        if resume_data.get('projects'):
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(37, 99, 235)
            pdf.cell(0, 10, 'PROJECTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            projects = resume_data.get('projects', '')
            projects = projects.replace('•', '-').replace('●', '-').replace('▶', '-')
            projects = ''.join(c for c in projects if ord(c) < 128)
            pdf.multi_cell(0, 6, projects)
            pdf.ln(5)
        
        # Certifications - USE HYPHENS
        if resume_data.get('certifications'):
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(37, 99, 235)
            pdf.cell(0, 10, 'CERTIFICATIONS', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            certs = resume_data.get('certifications', '')
            certs = certs.replace('•', '-').replace('●', '-').replace('▶', '-')
            certs = ''.join(c for c in certs if ord(c) < 128)
            pdf.multi_cell(0, 6, certs)
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        
        # Set flag for PDF export achievement
        update_pdf_export_flag()
        
        return temp_file.name
        
    except Exception as e:
        st.error(f"❌ PDF generation failed: {str(e)}")
        return None

# ============= TEST PDF FUNCTION =============
def test_pdf_generation():
    """Test function to verify PDF generation works"""
    if not PDF_AVAILABLE:
        print("❌ fpdf2 not installed. Run: pip install fpdf2")
        return None
        
    test_resume = {
        'name': 'Rahul Sharma',
        'email': 'rahul.sharma@example.com',
        'phone': '+91 98765 43210',
        'location': 'Bangalore, India',
        'summary': 'Python Developer with 2 years of experience in Django and REST APIs.',
        'skills': ['Python', 'Django', 'MySQL', 'Git', 'REST API', 'JavaScript'],
        'experience': [
            {
                'company': 'TCS',
                'duration': '2022-2024',
                'description': '- Developed Django web applications\n- Created REST APIs\n- Worked with MySQL database'
            }
        ],
        'education': 'B.Tech in Computer Science - VTU, 2022\nCGPA: 8.2/10',
        'projects': '- E-commerce Platform - Built with Django and React\n- REST API Service - FastAPI',
        'certifications': '- AWS Certified Cloud Practitioner\n- Python Institute Certification'
    }
    
    try:
        pdf_file = generate_ats_pdf(test_resume, 85, 'Python Developer')
        if pdf_file:
            print(f"✅ PDF generated successfully: {pdf_file}")
            print(f"📁 File saved at: {pdf_file}")
            return pdf_file
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None

# ============= VERSION INFO =============
def get_utils_version():
    return "2.2.0"  # Updated version with delete history functions

