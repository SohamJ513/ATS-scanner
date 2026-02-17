"""
ML-Enhanced ATS Scorer - Updated with semantic matching capabilities
"""
import re
from typing import Dict, List, Any
import numpy as np
from .embeddings import get_embedding_model
from .semantic_matcher import get_semantic_matcher  # NEW import

class MLEnhancedScanner:
    """
    ML-powered scanner using semantic understanding for better insights
    Runs alongside your existing ATS scanner without affecting it
    """
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.semantic_matcher = get_semantic_matcher()  # NEW semantic matcher
        self.ml_version = "2.0.0"  # Updated version
        
        # Enhanced skill categories with weights
        self.skill_categories = {
            'programming': {
                'skills': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'typescript'],
                'weight': 1.0,
                'synonyms': {
                    'python': ['python3', 'django', 'flask', 'fastapi'],
                    'java': ['j2ee', 'spring', 'spring boot', 'hibernate'],
                    'javascript': ['js', 'es6', 'node.js', 'react.js', 'angular.js']
                }
            },
            'web_frameworks': {
                'skills': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express'],
                'weight': 0.9
            },
            'database': {
                'skills': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'cassandra'],
                'weight': 0.9
            },
            'cloud_devops': {
                'skills': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
                'weight': 1.0
            },
            'data_science': {
                'skills': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'],
                'weight': 1.0
            },
            'mobile': {
                'skills': ['android', 'ios', 'kotlin', 'swift', 'flutter', 'react native'],
                'weight': 0.8
            },
            'testing': {
                'skills': ['junit', 'selenium', 'pytest', 'jest', 'mocha', 'cypress'],
                'weight': 0.7
            },
            'soft_skills': {
                'skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'analytical', 'critical thinking'],
                'weight': 0.6
            }
        }
    
    def get_semantic_score(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Enhanced ML-based semantic understanding using semantic matcher"""
        
        # Get semantic similarity from the matcher
        similarity = self.semantic_matcher.calculate_semantic_similarity(resume_text, job_text)
        
        # Get key phrases from resume
        key_phrases = self.semantic_matcher.extract_key_phrases(resume_text, 5)
        
        # Get job key phrases for comparison
        job_phrases = self.semantic_matcher.extract_key_phrases(job_text, 5)
        
        # Calculate section-wise scores
        section_scores = {}
        sentences = resume_text.split('.')
        for sentence in sentences[:10]:  # Check first 10 sentences
            if len(sentence.strip()) > 30:
                sent_sim = self.semantic_matcher.calculate_semantic_similarity(sentence, job_text)
                if sent_sim > 0.6:
                    section_scores[sentence[:50]] = round(sent_sim * 100, 1)
        
        return {
            "semantic_similarity": round(similarity * 100, 2),
            "interpretation": self._interpret_similarity(similarity),
            "key_phrases": key_phrases,
            "job_key_phrases": job_phrases,  # NEW
            "strong_matches": list(section_scores.keys())[:3] if section_scores else [],
            "ml_version": self.ml_version
        }
    
    def get_skill_intelligence(self, resume_skills: List[str], job_text: str) -> Dict[str, Any]:
        """Enhanced skill intelligence using semantic matching"""
        
        if not resume_skills:
            return {
                "skill_gaps": [],
                "suggested_skills": [],
                "gap_count": 0,
                "skill_match_score": 0,
                "top_matching_skills": []
            }
        
        # Extract potential skills from job description using semantic matcher
        job_phrases = self.semantic_matcher.extract_key_phrases(job_text, 20)
        
        skill_gaps = []
        skill_suggestions = []
        matched_skills = []
        
        # Check each job phrase against resume skills
        for phrase in job_phrases:
            found = False
            best_match = None
            best_score = 0
            
            for res_skill in resume_skills:
                # Use semantic matching to find related skills
                if self.semantic_matcher.find_similar_skills(phrase, res_skill, threshold=0.65):
                    found = True
                    matched_skills.append({
                        'job_skill': phrase,
                        'resume_skill': res_skill,
                        'match_score': best_score
                    })
                    break
            
            if not found:
                skill_gaps.append(phrase)
                
                # Suggest related skills from categories
                for category, data in self.skill_categories.items():
                    category_skills = data['skills'] if isinstance(data, dict) else data
                    for cat_skill in category_skills:
                        if self.semantic_matcher.find_similar_skills(phrase, cat_skill, threshold=0.5):
                            skill_suggestions.append(cat_skill)
                            break
        
        # Calculate overall skill match score
        total_relevant = len(job_phrases)
        matched_count = len(matched_skills)
        skill_match_score = (matched_count / total_relevant) * 100 if total_relevant > 0 else 0
        
        return {
            "skill_gaps": list(set(skill_gaps))[:8],
            "suggested_skills": list(set(skill_suggestions))[:5],
            "gap_count": len(skill_gaps),
            "skill_match_score": round(skill_match_score, 1),
            "top_matching_skills": [m['resume_skill'] for m in matched_skills[:3]],
            "detailed_matches": matched_skills[:5]
        }
    
    def get_experience_insights(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Enhanced experience analysis using semantic matching"""
        
        # Extract experience-related sentences
        exp_keywords = ['experience', 'worked', 'work', 'developed', 'led', 'managed', 'created']
        
        exp_sentences = []
        sentences = resume_text.split('.')
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in exp_keywords):
                exp_sentences.append(sentence.strip())
        
        # Check job for experience requirements
        job_has_exp = any(kw in job_text.lower() for kw in ['experience', 'years', 'yr'])
        
        # Calculate experience relevance score
        exp_relevance = 0
        if exp_sentences:
            # Get embedding of experience section
            exp_text = '. '.join(exp_sentences[:3])
            exp_relevance = self.semantic_matcher.calculate_semantic_similarity(exp_text, job_text)
        
        # Extract years of experience mentioned
        years_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)'
        resume_years = re.findall(years_pattern, resume_text.lower())
        job_years = re.findall(years_pattern, job_text.lower())
        
        return {
            "has_experience_section": len(exp_sentences) > 0,
            "job_requires_experience": job_has_exp,
            "experience_relevance": round(exp_relevance * 100, 1),
            "experience_sentences": exp_sentences[:2],
            "resume_years_mentioned": resume_years,
            "job_years_required": job_years,
            "experience_match": exp_relevance > 0.6
        }
    
    def get_education_insights(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """NEW: Education insights using semantic matching"""
        
        education_keywords = ['b.tech', 'b.e', 'm.tech', 'mca', 'b.sc', 'm.sc', 'phd', 'bachelor', 'master']
        
        # Find education section
        edu_sentences = []
        sentences = resume_text.split('\n')
        in_edu = False
        
        for sentence in sentences:
            lower = sentence.lower()
            if 'education' in lower or 'qualification' in lower:
                in_edu = True
                continue
            if in_edu and len(sentence.strip()) > 10:
                edu_sentences.append(sentence)
                if len(edu_sentences) >= 5:
                    break
            elif in_edu and any(kw in lower for kw in ['experience', 'skills', 'project']):
                in_edu = False
        
        # Check job for education requirements
        job_requires_edu = any(kw in job_text.lower() for kw in education_keywords)
        
        # Calculate education relevance
        edu_relevance = 0
        if edu_sentences:
            edu_text = ' '.join(edu_sentences)
            edu_relevance = self.semantic_matcher.calculate_semantic_similarity(edu_text, job_text)
        
        return {
            "has_education_section": len(edu_sentences) > 0,
            "job_requires_education": job_requires_edu,
            "education_relevance": round(edu_relevance * 100, 1),
            "education_details": edu_sentences[:2],
            "education_match": edu_relevance > 0.5
        }
    
    def get_semantic_gaps(self, resume_text: str, job_text: str) -> List[Dict[str, Any]]:
        """NEW: Identify semantic gaps between resume and job"""
        
        # Get key phrases from both
        resume_phrases = self.semantic_matcher.extract_key_phrases(resume_text, 10)
        job_phrases = self.semantic_matcher.extract_key_phrases(job_text, 10)
        
        gaps = []
        for job_phrase in job_phrases:
            found = False
            for res_phrase in resume_phrases:
                similarity = self.semantic_matcher.calculate_semantic_similarity(job_phrase, res_phrase)
                if similarity > 0.7:
                    found = True
                    break
            
            if not found:
                # Find related skills to suggest
                suggestions = []
                for category, data in self.skill_categories.items():
                    category_skills = data['skills'] if isinstance(data, dict) else data
                    for skill in category_skills[:3]:
                        if self.semantic_matcher.find_similar_skills(job_phrase, skill, threshold=0.5):
                            suggestions.append(skill)
                
                gaps.append({
                    'missing_concept': job_phrase,
                    'importance': 'high' if len(job_phrase.split()) > 1 else 'medium',
                    'suggested_skills': list(set(suggestions))[:3]
                })
        
        return gaps[:5]
    
    def get_comprehensive_insights(self, resume_text: str, job_text: str,
                                  resume_skills: List[str]) -> Dict[str, Any]:
        """NEW: Comprehensive analysis combining all insights"""
        
        semantic = self.get_semantic_score(resume_text, job_text)
        skills = self.get_skill_intelligence(resume_skills, job_text)
        experience = self.get_experience_insights(resume_text, job_text)
        education = self.get_education_insights(resume_text, job_text)
        gaps = self.get_semantic_gaps(resume_text, job_text)
        
        # Calculate overall match score
        match_score = (
            semantic['semantic_similarity'] * 0.4 +
            skills['skill_match_score'] * 0.3 +
            experience['experience_relevance'] * 0.2 +
            education['education_relevance'] * 0.1
        )
        
        return {
            "overall_match_score": round(match_score, 1),
            "semantic_analysis": semantic,
            "skill_intelligence": skills,
            "experience_insights": experience,
            "education_insights": education,
            "semantic_gaps": gaps,
            "ml_version": self.ml_version,
            "note": "Comprehensive ML-powered insights using semantic understanding"
        }
    
    def _interpret_similarity(self, score: float) -> str:
        """Enhanced interpretation of similarity score"""
        if score > 0.85:
            return "🎯 Excellent semantic match - your resume perfectly aligns with the job"
        elif score > 0.75:
            return "✅ Strong semantic alignment - your experience matches well"
        elif score > 0.65:
            return "📈 Good semantic relevance - minor adjustments recommended"
        elif score > 0.5:
            return "📊 Moderate semantic match - consider tailoring your resume more"
        elif score > 0.35:
            return "🔧 Low semantic similarity - significant changes needed"
        else:
            return "⚠️ Very low semantic match - resume needs major restructuring"
    
    def get_ml_insights(self, resume_text: str, job_text: str, 
                       resume_skills: List[str]) -> Dict[str, Any]:
        """
        Main method - returns comprehensive ML insights
        Call this alongside your existing scanner for enhanced analysis
        """
        return self.get_comprehensive_insights(resume_text, job_text, resume_skills)

# For backward compatibility - simple insights
def get_simple_ml_insights(resume_text: str, job_text: str, 
                          resume_skills: List[str]) -> Dict[str, Any]:
    """Simpler version for backward compatibility"""
    scanner = get_ml_scanner()
    return {
        "semantic_analysis": scanner.get_semantic_score(resume_text, job_text),
        "skill_intelligence": scanner.get_skill_intelligence(resume_skills, job_text),
        "experience_insights": scanner.get_experience_insights(resume_text, job_text),
        "ml_version": scanner.ml_version,
        "note": "ML-powered insights using semantic understanding"
    }

# Singleton instance
_ml_scanner = None

def get_ml_scanner():
    """Get or create the ML scanner singleton"""
    global _ml_scanner
    if _ml_scanner is None:
        _ml_scanner = MLEnhancedScanner()
    return _ml_scanner