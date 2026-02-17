import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
from datetime import datetime

# Import our new semantic matcher
try:
    from .semantic_matcher import get_semantic_matcher
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠️ Semantic matcher not available. Using keyword matching only.")

class ATSScanner:
    def __init__(self):
        # ATS-critical sections
        self.critical_sections = ['skills', 'experience', 'education']
        self.optional_sections = ['projects', 'certifications', 'achievements', 'summary']
        
        # Initialize semantic matcher if available
        self.semantic_matcher = None
        if SEMANTIC_AVAILABLE:
            try:
                self.semantic_matcher = get_semantic_matcher()
                print("✅ Semantic matcher initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize semantic matcher: {e}")
                self.semantic_matcher = None
        
        # ATS-unfriendly elements - more forgiving
        self.unfriendly_elements = {
            "headers_footers": r'(page \d+|\d+ of \d+)',
            "tables": r'┌|┐|└|┘|├|┤|┬|┴|┼',
            "images": r'\[image\]|\[figure\]',
            "columns": r'\s{20,}'  # Increased threshold
        }
        
        # Skill variations for fallback
        self.skill_variations = {
            'python': ['python', 'python3', 'django', 'flask', 'fastapi'],
            'java': ['java', 'j2ee', 'spring', 'spring boot', 'hibernate'],
            'javascript': ['javascript', 'js', 'es6', 'node', 'node.js', 'react', 'angular', 'vue'],
            'sql': ['sql', 'mysql', 'postgresql', 'database', 'rdbms'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
            'azure': ['azure', 'microsoft azure', 'cloud'],
            'docker': ['docker', 'container', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s', 'container orchestration'],
            'git': ['git', 'github', 'gitlab', 'version control'],
            'devops': ['devops', 'ci/cd', 'jenkins', 'github actions'],
        }
    
    def calculate_ats_score(self, resume_data: Dict, job_description: str) -> Dict:
        """Calculate comprehensive ATS score using semantic matching if available"""
        resume_text = resume_data['raw_text']
        
        # Calculate individual scores
        scores = {
            "section_presence": self._section_presence_score(resume_data.get('sections', {})),
            "formatting": self._formatting_score(resume_text),
            "skill_match": self._skill_match_score(resume_data.get('skills', []), job_description),
            "experience_match": self._experience_match_score(resume_data.get('experience', []), job_description),
            "education_match": self._education_match_score(resume_data.get('sections', {}).get('education', '')),
            "certification_match": self._certification_match_score(resume_data.get('certifications', []), job_description)
        }
        
        # Add semantic similarity score if available
        if self.semantic_matcher:
            semantic_score = self.semantic_matcher.calculate_semantic_similarity(
                resume_text, job_description
            )
            scores["semantic_match"] = semantic_score
            # Extract key phrases for feedback
            key_phrases = self.semantic_matcher.extract_key_phrases(job_description, 5)
        else:
            # Fallback to keyword similarity
            scores["keyword_match"] = self._keyword_similarity(resume_text, job_description)
            key_phrases = []
        
        # IMPROVED WEIGHTS - semantic matching gets highest weight when available
        if self.semantic_matcher:
            weights = {
                "semantic_match": 0.35,      # 35% - Understanding meaning
                "skill_match": 0.25,          # 25% - Skills are important
                "experience_match": 0.15,      # 15% - Experience relevance
                "section_presence": 0.10,      # 10% - Basic requirement
                "formatting": 0.05,            # 5%  - Minor penalty
                "education_match": 0.05,       # 5%  - Education matters
                "certification_match": 0.05    # 5%  - Bonus points
            }
        else:
            # Fallback weights without semantic
            weights = {
                "keyword_match": 0.25,
                "skill_match": 0.25,
                "experience_match": 0.20,
                "section_presence": 0.10,
                "formatting": 0.05,
                "education_match": 0.10,
                "certification_match": 0.05
            }
        
        # Calculate weighted score
        final_score = 0
        score_components = {}
        
        for key, score in scores.items():
            if key in weights:
                weighted = score * weights[key] * 100
                final_score += weighted
                score_components[key] = round(weighted, 1)
        
        # Apply bonus for exceptional resumes
        bonus = self._calculate_bonus_points(resume_data, scores)
        final_score = min(final_score + bonus, 100)
        final_score = round(final_score, 1)
        
        # Get missing keywords (using semantic if available)
        if self.semantic_matcher:
            missing_keywords = self._extract_missing_keywords_semantic(resume_text, job_description)
        else:
            missing_keywords = self._extract_missing_keywords(resume_text, job_description)
        
        # Generate enhanced feedback
        feedback = self._generate_enhanced_feedback(scores, resume_data, job_description, final_score)
        
        result = {
            "overall_score": final_score,
            "component_scores": score_components,
            "feedback": feedback,
            "missing_keywords": missing_keywords,
            "bonus_points": bonus,
            "score_breakdown": self._get_score_breakdown(scores, weights, bonus)
        }
        
        # Add semantic key phrases if available
        if key_phrases:
            result["key_phrases"] = key_phrases
        
        return result
    
    def _keyword_similarity(self, resume: str, jd: str) -> float:
        """Fallback keyword similarity using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=100,
                ngram_range=(1, 2),
                min_df=1
            )
            tfidf_matrix = vectorizer.fit_transform([resume, jd])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return 0.3 + (float(similarity[0][0]) * 0.7)
        except Exception as e:
            print(f"Keyword similarity error: {e}")
            return 0.4
    
    def _extract_missing_keywords_semantic(self, resume: str, jd: str) -> List[str]:
        """Extract missing keywords using semantic understanding"""
        if not self.semantic_matcher:
            return self._extract_missing_keywords(resume, jd)
        
        try:
            # Get key phrases from job description
            key_phrases = self.semantic_matcher.extract_key_phrases(jd, 15)
            
            missing = []
            for phrase in key_phrases:
                # Check if phrase or its semantic equivalent exists in resume
                if not self.semantic_matcher.find_similar_skills(phrase, resume, threshold=0.7):
                    missing.append(phrase)
            
            return missing[:10]
        except Exception as e:
            print(f"Semantic keyword extraction error: {e}")
            return self._extract_missing_keywords(resume, jd)
    
    def _skill_match_score(self, skills: List[str], jd: str) -> float:
        """Calculate skill match using semantic similarity if available"""
        if not skills:
            return 0.2
        
        try:
            if self.semantic_matcher:
                # Use semantic matching
                matched = 0
                for skill in skills[:15]:
                    if self.semantic_matcher.find_similar_skills(skill, jd):
                        matched += 1
                return 0.2 + (matched / max(len(skills), 1) * 0.8)
            else:
                # Fallback to keyword matching with variations
                jd_lower = jd.lower()
                matched_skills = []
                partial_matches = []
                
                for skill in skills:
                    skill_lower = skill.lower()
                    
                    # Exact match
                    if skill_lower in jd_lower:
                        matched_skills.append(skill)
                        continue
                    
                    # Check for skill variations
                    found = False
                    for base_skill, variations in self.skill_variations.items():
                        if skill_lower in variations or base_skill in skill_lower:
                            if any(var in jd_lower for var in variations[:2]):
                                partial_matches.append(skill)
                                found = True
                                break
                    
                    if not found:
                        # Partial word match
                        words = skill_lower.split()
                        for word in words:
                            if len(word) > 3 and word in jd_lower:
                                partial_matches.append(skill)
                                break
                
                exact_score = len(matched_skills) / max(len(skills), 1) * 0.7
                partial_score = len(set(partial_matches)) / max(len(skills), 1) * 0.3
                return min(exact_score + partial_score + 0.2, 1.0)
        except Exception as e:
            print(f"Skill match error: {e}")
            return 0.3
    
    def _section_presence_score(self, sections: Dict) -> float:
        """Score based on presence of critical and optional sections"""
        try:
            # Critical sections (70% of score)
            present_critical = 0
            for section in self.critical_sections:
                if section in sections and len(str(sections.get(section, '')).strip()) > 20:
                    present_critical += 1
            
            critical_score = present_critical / len(self.critical_sections) if self.critical_sections else 0
            
            # Optional sections (30% of score)
            present_optional = 0
            for section in self.optional_sections:
                if section in sections and len(str(sections.get(section, '')).strip()) > 20:
                    present_optional += 1
            
            optional_score = min(present_optional / len(self.optional_sections) if self.optional_sections else 0, 1.0)
            
            # Combine scores (critical sections are more important)
            return (critical_score * 0.7) + (optional_score * 0.3)
        except Exception as e:
            print(f"Section presence error: {e}")
            return 0.5
    
    def _formatting_score(self, text: str) -> float:
        """Check for ATS-unfriendly formatting - MORE FORGIVING"""
        try:
            penalty = 0
            total_checks = len(self.unfriendly_elements)
            
            for element, pattern in self.unfriendly_elements.items():
                if re.search(pattern, text, re.IGNORECASE):
                    penalty += 0.3  # Reduced penalty
            
            # Non-ASCII characters - less penalty
            non_ascii = re.findall(r'[^\x00-\x7F]', text)
            if non_ascii:
                penalty += min(0.2, len(non_ascii) * 0.01)  # Small penalty per character
            
            # Check for PDF-friendly formatting
            if text.count('\n') > 50:  # Good line breaks
                penalty -= 0.1
            
            score = max(0.7, 1.0 - penalty)  # Minimum 0.7
            return min(score, 1.0)  # Cap at 1.0
        except Exception as e:
            print(f"Formatting score error: {e}")
            return 0.8
    
    def _experience_match_score(self, experience: List[Dict], jd: str) -> float:
        """Score based on experience relevance - FIXED for None values"""
        try:
            jd_lower = jd.lower() if jd else ""
            
            # Extract required years from JD
            years_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?|yr)'
            jd_years_match = re.search(years_pattern, jd_lower)
            required_years = int(jd_years_match.group(1)) if jd_years_match else 2
            
            # Base score for freshers
            if not experience:
                if 'fresher' in jd_lower or '0 years' in jd_lower:
                    return 0.9  # Fresher applying for fresher role
                return 0.3  # Fresher applying for experienced role
            
            # Calculate total years of experience
            total_years = 0
            relevance_score = 0
            leadership_score = 0
            
            for exp in experience[:3]:  # Consider top 3 experiences
                # SAFELY get duration - handle None values
                duration = exp.get('duration')
                if duration is None:
                    duration = ""
                else:
                    duration = str(duration).lower()
                
                # SAFELY get description - handle None values
                description = exp.get('description')
                if description is None:
                    description = ""
                else:
                    description = str(description).lower()
                
                # Extract years from duration
                if 'present' in duration or 'current' in duration:
                    year_match = re.search(r'(\d{4})', duration)
                    if year_match:
                        start_year = int(year_match.group(1))
                        years = datetime.now().year - start_year
                        total_years += years
                else:
                    year_range = re.findall(r'(\d{4})', duration)
                    if len(year_range) >= 2:
                        total_years += int(year_range[1]) - int(year_range[0])
                    elif len(year_range) == 1:
                        total_years += 1  # Assume 1 year if only start date
                
                # Check for relevance using semantic if available
                if self.semantic_matcher and description:
                    try:
                        if self.semantic_matcher.find_similar_skills(description, jd, threshold=0.6):
                            relevance_score += 0.2
                    except:
                        # Simple relevance check as fallback
                        if any(word in jd_lower for word in description.split()[:5] if word):
                            relevance_score += 0.2
                else:
                    # Simple relevance check
                    if description and any(word in jd_lower for word in description.split()[:5] if word):
                        relevance_score += 0.2
                
                # Check for leadership
                leadership_keywords = ['lead', 'senior', 'manager', 'head', 'architect', 'mentor']
                if any(kw in description for kw in leadership_keywords):
                    leadership_score += 0.1
            
            # Calculate experience score
            if total_years >= required_years:
                exp_score = 1.0
            else:
                exp_score = 0.5 + (total_years / required_years * 0.5) if required_years > 0 else 0.5
            
            # Combine scores
            total_score = exp_score * 0.6 + min(relevance_score, 0.3) + min(leadership_score, 0.1)
            
            return min(total_score, 1.0)
            
        except Exception as e:
            print(f"Experience match error: {e}")
            return 0.5
    
    def _education_match_score(self, education_text: str) -> float:
        """Score based on education - IMPROVED"""
        try:
            if not education_text or len(str(education_text).strip()) < 10:
                return 0.3  # Base score for missing education
            
            education_lower = str(education_text).lower()
            
            # Check for degree types and quality
            degree_score = 0
            cgpa_score = 0
            
            # Bachelor's degrees
            bachelors = ['b.tech', 'b.e', 'b.sc', 'bca', 'bachelor']
            for degree in bachelors:
                if degree in education_lower:
                    degree_score = 0.6
                    break
            
            # Master's degrees
            masters = ['m.tech', 'm.e', 'm.sc', 'mca', 'master']
            for degree in masters:
                if degree in education_lower:
                    degree_score = 0.8
                    break
            
            # PhD
            if 'phd' in education_lower or 'doctor' in education_lower:
                degree_score = 1.0
            
            # Check for CGPA/percentage
            cgpa_pattern = r'cgpa[:\s]*(\d+\.?\d*)'
            percentage_pattern = r'(\d{2,3})%'
            
            cgpa_match = re.search(cgpa_pattern, education_lower)
            if cgpa_match:
                cgpa = float(cgpa_match.group(1))
                if cgpa >= 8.0:
                    cgpa_score = 0.3
                elif cgpa >= 7.0:
                    cgpa_score = 0.2
                elif cgpa >= 6.0:
                    cgpa_score = 0.1
            
            percentage_match = re.search(percentage_pattern, education_lower)
            if percentage_match:
                percentage = int(percentage_match.group(1))
                if percentage >= 80:
                    cgpa_score = 0.3
                elif percentage >= 70:
                    cgpa_score = 0.2
                elif percentage >= 60:
                    cgpa_score = 0.1
            
            return min(degree_score + cgpa_score, 1.0)
        except Exception as e:
            print(f"Education match error: {e}")
            return 0.4
    
    def _certification_match_score(self, certifications: List, jd: str) -> float:
        """Score based on certifications"""
        try:
            if not certifications:
                return 0.2  # Base score
            
            jd_lower = jd.lower() if jd else ""
            matched = 0
            
            # Process certifications (could be list of strings or dicts)
            cert_list = []
            for cert in certifications:
                if isinstance(cert, dict):
                    cert_text = ' '.join([str(v) for v in cert.values()]).lower()
                else:
                    cert_text = str(cert).lower() if cert else ""
                if cert_text:
                    cert_list.append(cert_text)
            
            # Check for cloud certifications
            cloud_certs = ['aws', 'azure', 'gcp', 'cloud']
            for cert in cert_list:
                if any(cloud in cert for cloud in cloud_certs):
                    if any(cloud in jd_lower for cloud in cloud_certs):
                        matched += 1.5  # Extra weight for cloud certs
            
            # Check for other certifications
            for cert in cert_list[:5]:  # Check top 5
                cert_words = set(cert.split())
                for word in cert_words:
                    if len(word) > 3 and word in jd_lower:
                        matched += 0.5
                        break
            
            return min(0.3 + (matched * 0.1), 1.0)
        except Exception as e:
            print(f"Certification match error: {e}")
            return 0.3
    
    def _calculate_bonus_points(self, resume_data: Dict, scores: Dict) -> float:
        """Calculate bonus points for exceptional resumes"""
        try:
            bonus = 0
            
            # Skills bonus
            skills_count = len(resume_data.get('skills', []))
            if skills_count >= 20:
                bonus += 5
            elif skills_count >= 15:
                bonus += 3
            elif skills_count >= 10:
                bonus += 1
            
            # Certifications bonus
            certs = resume_data.get('certifications', [])
            if len(certs) >= 5:
                bonus += 4
            elif len(certs) >= 3:
                bonus += 2
            
            # Experience bonus
            if scores.get('experience_match', 0) > 0.9:
                bonus += 3
            elif scores.get('experience_match', 0) > 0.8:
                bonus += 1
            
            # Education bonus
            if scores.get('education_match', 0) > 0.8:
                bonus += 2
            elif scores.get('education_match', 0) > 0.7:
                bonus += 1
            
            # Semantic bonus (if available and high)
            if scores.get('semantic_match', 0) > 0.85:
                bonus += 3
            elif scores.get('semantic_match', 0) > 0.75:
                bonus += 1
            
            return min(bonus, 20)  # Max 20 bonus points
        except Exception as e:
            print(f"Bonus calculation error: {e}")
            return 0
    
    def _extract_missing_keywords(self, resume: str, jd: str) -> List[str]:
        """Fallback keyword extraction"""
        try:
            resume_lower = resume.lower() if resume else ""
            jd_lower = jd.lower() if jd else ""
            
            # Extract meaningful keywords
            words = re.findall(r'\b[a-zA-Z]{3,}\b', jd_lower)
            
            # Stopwords
            stopwords = {
                'the', 'and', 'for', 'with', 'this', 'that', 'have', 'from', 
                'will', 'your', 'would', 'should', 'candidate', 'position', 
                'company', 'work', 'experience', 'skill', 'ability', 'knowledge',
                'looking', 'hiring', 'join', 'team', 'role', 'job', 'required',
                'preferred', 'qualifications', 'responsibilities', 'must', 'able'
            }
            
            # Technical keywords to prioritize
            tech_priority = [
                'python', 'java', 'javascript', 'react', 'angular', 'node',
                'django', 'flask', 'spring', 'aws', 'azure', 'docker',
                'kubernetes', 'sql', 'mongodb', 'git', 'jenkins',
                'machine learning', 'data science', 'tensorflow', 'pytorch'
            ]
            
            keywords = [word for word in words if word not in stopwords and len(word) > 2]
            word_counts = Counter(keywords)
            
            # Score and rank missing keywords
            missing_scores = []
            for word, count in word_counts.most_common(30):
                if word not in resume_lower:
                    # Prioritize technical keywords
                    priority = 3 if word in tech_priority else 1
                    score = count * priority
                    missing_scores.append((word, score))
            
            # Sort by score and return top keywords
            missing_scores.sort(key=lambda x: x[1], reverse=True)
            return [word for word, _ in missing_scores[:10]]
        except Exception as e:
            print(f"Missing keywords extraction error: {e}")
            return []
    
    def _generate_enhanced_feedback(self, scores: Dict, resume_data: Dict, jd: str, final_score: float) -> List[str]:
        """Generate enhanced, more specific feedback"""
        feedback = []
        
        try:
            # Overall score interpretation
            if final_score >= 90:
                feedback.append("🎯 **Outstanding!** Your resume is highly optimized and competitive for this role.")
            elif final_score >= 80:
                feedback.append("✅ **Excellent!** Your resume is very strong with minor room for improvement.")
            elif final_score >= 70:
                feedback.append("📈 **Good foundation!** A few strategic improvements will make you highly competitive.")
            elif final_score >= 60:
                feedback.append("🔧 **Getting there!** Several key improvements are needed.")
            else:
                feedback.append("💪 **Room to grow!** Let's work on making your resume more competitive.")
            
            # Semantic match feedback (if available)
            if 'semantic_match' in scores:
                if scores['semantic_match'] < 0.5:
                    feedback.append("🧠 **Semantic match:** Your resume doesn't align well with the job meaning. Try using similar language.")
                elif scores['semantic_match'] < 0.7:
                    feedback.append("📊 **Semantic match:** Good alignment, but could be more tailored.")
                else:
                    feedback.append("✨ **Semantic match:** Excellent alignment with job requirements!")
            
            # Keyword match feedback (fallback)
            elif 'keyword_match' in scores:
                if scores['keyword_match'] < 0.5:
                    feedback.append("📝 **Keywords:** Add more specific technical keywords from the job description.")
                elif scores['keyword_match'] < 0.7:
                    feedback.append("📊 **Keyword density:** Good, but could include more variations.")
            
            # Skill match feedback
            if scores.get('skill_match', 0) < 0.6:
                missing = self._extract_missing_keywords(resume_data.get('raw_text', ''), jd)
                if missing:
                    feedback.append(f"💡 **Skills to add:** {', '.join(missing[:5])}")
            
            # Skills count feedback
            skills_count = len(resume_data.get('skills', []))
            if skills_count < 8:
                feedback.append(f"📚 **Skills section:** List at least 8-10 relevant skills. Currently have {skills_count}.")
            elif skills_count < 12:
                feedback.append(f"✅ **Skills section:** Good ({skills_count} skills). Consider adding more emerging technologies.")
            
            # Experience feedback
            if scores.get('experience_match', 0) < 0.6:
                if not resume_data.get('experience'):
                    feedback.append("💼 **Experience:** Add internships, projects, or relevant coursework.")
                else:
                    feedback.append("📈 **Experience:** Quantify your achievements with metrics (%, ₹, numbers, time saved).")
            
            # Formatting feedback
            if scores.get('formatting', 1.0) < 0.8:
                feedback.append("📄 **Formatting:** Use standard fonts (Arial/Calibri), avoid tables, save as PDF.")
            
            # Education feedback
            if scores.get('education_match', 0) < 0.6:
                feedback.append("🎓 **Education:** Clearly list your degree with specialization, institution, and CGPA/percentage.")
            
            # Certification feedback
            certs = resume_data.get('certifications', [])
            if len(certs) < 2:
                cloud_in_jd = any(word in jd.lower() for word in ['aws', 'azure', 'gcp', 'cloud'])
                if cloud_in_jd:
                    feedback.append("☁️ **Certifications:** Job mentions cloud - consider adding AWS/Azure/Google Cloud certifications.")
                else:
                    feedback.append("📜 **Certifications:** Consider adding relevant certifications to stand out.")
            
        except Exception as e:
            print(f"Feedback generation error: {e}")
            feedback.append("📊 **Analysis complete.** Review your resume for improvements.")
        
        return feedback[:6]  # Limit to top 6 feedback items
    
    def _get_score_breakdown(self, scores: Dict, weights: Dict, bonus: float) -> Dict:
        """Get detailed score breakdown for display"""
        breakdown = {}
        
        try:
            for key, weight in weights.items():
                if key in scores:
                    display_name = key.replace('_', ' ').title()
                    raw_score = round(scores[key] * 100, 1)
                    contribution = round(scores[key] * weight * 100, 1)
                    
                    breakdown[display_name] = {
                        'score': raw_score,
                        'weight': f"{weight*100:.0f}%",
                        'contribution': contribution,
                        'max_possible': round(weight * 100, 1)
                    }
            
            if bonus > 0:
                breakdown['Bonus Points'] = {
                    'score': bonus,
                    'weight': 'Bonus',
                    'contribution': bonus,
                    'max_possible': 20
                }
        except Exception as e:
            print(f"Score breakdown error: {e}")
        
        return breakdown