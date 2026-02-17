# ============================================
# ACHIEVEMENTS.PY - Gamification & Progress Tracking
# ============================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import load_scan_history

ACHIEVEMENTS = {
    "first_scan": {
        "name": "🚀 First Steps",
        "description": "Analyzed your first resume",
        "icon": "🎯",
        "points": 10
    },
    "score_80": {
        "name": "💪 ATS Ready",
        "description": "Achieved ATS score of 80+",
        "icon": "🎯",
        "points": 25
    },
    "score_90": {
        "name": "🏆 ATS Master",
        "description": "Achieved ATS score of 90+",
        "icon": "🏆",
        "points": 50
    },
    "streak_5": {
        "name": "🔥 Getting Serious",
        "description": "Analyzed resumes 5 days in a row",
        "icon": "🔥",
        "points": 30
    },
    "streak_10": {
        "name": "⚡ On Fire",
        "description": "Analyzed resumes 10 days in a row",
        "icon": "⚡",
        "points": 75
    },
    "skills_10": {
        "name": "📚 Skill Stacker",
        "description": "Added 10+ skills to your resume",
        "icon": "📚",
        "points": 20
    },
    "skills_20": {
        "name": "🧠 Knowledge Hub",
        "description": "Added 20+ skills to your resume",
        "icon": "🧠",
        "points": 40
    },
    "companies_5": {
        "name": "🏢 Company Explorer",
        "description": "Scored 5+ companies in simulator",
        "icon": "🏢",
        "points": 35
    },
    "ml_enabled": {
        "name": "🤖 AI Pioneer",
        "description": "Enabled ML-powered insights",
        "icon": "🤖",
        "points": 45
    },
    "pdf_export": {
        "name": "📄 Resume Pro",
        "description": "Exported your first PDF resume",
        "icon": "📄",
        "points": 15
    },
    "scan_10": {
        "name": "📊 Analysis Expert",
        "description": "Completed 10 resume scans",
        "icon": "📊",
        "points": 30
    },
    "scan_25": {
        "name": "🎓 ATS Scholar",
        "description": "Completed 25 resume scans",
        "icon": "🎓",
        "points": 60
    },
    "company_all": {
        "name": "🏆 Company Master",
        "description": "Tried all company simulators",
        "icon": "🏆",
        "points": 100
    }
}

def check_achievements(user_id=None):
    """Check and return unlocked achievements"""
    
    df = load_scan_history(limit=100)
    unlocked = []
    
    if df.empty:
        return []
    
    # First scan achievement
    if len(df) >= 1:
        unlocked.append("first_scan")
    
    # Scan count achievements
    if len(df) >= 25:
        unlocked.append("scan_25")
    elif len(df) >= 10:
        unlocked.append("scan_10")
    
    # Score achievements
    max_score = df['ats_score'].max()
    if max_score >= 90:
        unlocked.append("score_90")
    elif max_score >= 80:
        unlocked.append("score_80")
    
    # Streak achievement - FIXED with proper pandas import
    if not df.empty:
        dates = pd.to_datetime(df['date']).dt.date.unique()
        if len(dates) >= 10:
            unlocked.append("streak_10")
        elif len(dates) >= 5:
            unlocked.append("streak_5")
    
    # Skills achievements
    max_skills = df['skills_found'].max()
    if max_skills >= 20:
        unlocked.append("skills_20")
    elif max_skills >= 10:
        unlocked.append("skills_10")
    
    # Company simulator achievement
    if 'company_sim_count' in st.session_state:
        count = st.session_state.company_sim_count
        if count >= 10:
            unlocked.append("company_all")
        elif count >= 5:
            unlocked.append("companies_5")
    
    # ML achievement
    if st.session_state.get('enable_ml', False):
        unlocked.append("ml_enabled")
    
    # PDF export achievement
    if 'pdf_exported' in st.session_state and st.session_state.pdf_exported:
        unlocked.append("pdf_export")
    
    return list(set(unlocked))  # Remove duplicates

def calculate_user_level(achievements):
    """Calculate user level based on achievement points"""
    points = sum(ACHIEVEMENTS[a]['points'] for a in achievements if a in ACHIEVEMENTS)
    
    if points < 50:
        level = 1
        title = "🥉 Resume Rookie"
    elif points < 150:
        level = 2
        title = "🥈 Job Seeker"
    elif points < 300:
        level = 3
        title = "🥇 ATS Apprentice"
    elif points < 500:
        level = 4
        title = "💎 ATS Expert"
    else:
        level = 5
        title = "👑 ATS Master"
    
    next_level_points = [50, 150, 300, 500, 1000]
    points_to_next = next((p for p in next_level_points if p > points), 1000) - points
    
    return {
        "level": level,
        "title": title,
        "points": points,
        "points_to_next": points_to_next
    }

def display_achievements():
    """Display achievements in sidebar"""
    
    achievements = check_achievements()
    level_info = calculate_user_level(achievements)
    
    st.markdown("### 🏆 Your Progress")
    
    # Level card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 2rem;">{level_info['title'][0]}</span>
                <span style="font-weight: 600; margin-left: 0.5rem;">{level_info['title']}</span>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px;">
                Level {level_info['level']}
            </div>
        </div>
        <div style="margin-top: 0.5rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                <span>{level_info['points']} points</span>
                <span>{level_info['points_to_next']} to next level</span>
            </div>
            <div style="background: rgba(255,255,255,0.3); height: 6px; border-radius: 3px; margin-top: 0.3rem;">
                <div style="background: white; width: {min(100, (level_info['points'] / 500) * 100)}%; height: 6px; border-radius: 3px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats summary
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.metric("🏆 Achievements", len(achievements))
    with stats_col2:
        st.metric("⭐ Level", level_info['level'])
    with stats_col3:
        st.metric("💯 Points", level_info['points'])
    
    # Recent achievements
    if achievements:
        st.markdown("**📌 Recent Achievements:**")
        recent = achievements[-3:]  # Last 3
        for ach in recent:
            if ach in ACHIEVEMENTS:
                a = ACHIEVEMENTS[ach]
                st.markdown(f"{a['icon']} **{a['name']}**  \n{a['description']}  \n<small>+{a['points']} points</small>", unsafe_allow_html=True)
    else:
        st.info("📌 Analyze your first resume to unlock achievements!")
    
    # Achievement progress bars
    st.markdown("---")
    st.markdown("**📊 Next Achievements:**")
    
    # Progress to next scan milestone
    df = load_scan_history(limit=100)
    scan_count = len(df)
    if scan_count < 10:
        progress = scan_count / 10
        st.progress(progress, text=f"📊 {scan_count}/10 scans - Unlock 'Analysis Expert'")
    elif scan_count < 25:
        progress = scan_count / 25
        st.progress(progress, text=f"🎓 {scan_count}/25 scans - Unlock 'ATS Scholar'")
    
    # Progress to next streak
    if not df.empty:
        dates = pd.to_datetime(df['date']).dt.date.unique()
        streak = len(dates)
        if streak < 5:
            progress = streak / 5
            st.progress(progress, text=f"🔥 {streak}/5 days - Unlock 'Getting Serious'")
        elif streak < 10:
            progress = streak / 10
            st.progress(progress, text=f"⚡ {streak}/10 days - Unlock 'On Fire'")
    
    # Progress to next skills milestone
    max_skills = df['skills_found'].max() if not df.empty else 0
    if max_skills < 10:
        progress = max_skills / 10
        st.progress(progress, text=f"📚 {max_skills}/10 skills - Unlock 'Skill Stacker'")
    elif max_skills < 20:
        progress = max_skills / 20
        st.progress(progress, text=f"🧠 {max_skills}/20 skills - Unlock 'Knowledge Hub'")