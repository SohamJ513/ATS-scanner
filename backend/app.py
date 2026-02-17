from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Optional, Dict, List
import uuid
import sys
import logging
import traceback

# ============= SETUP LOGGING =============
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= WINDOWS-SPECIFIC PATH FIX =============
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import using importlib
import importlib.util

ML_DIR = os.path.join(current_dir, 'ml')
PARSER_PATH = os.path.join(ML_DIR, 'parser.py')
SCORER_PATH = os.path.join(ML_DIR, 'scorer.py')

# Load parser module
try:
    parser_spec = importlib.util.spec_from_file_location("ml.parser", PARSER_PATH)
    parser_module = importlib.util.module_from_spec(parser_spec)
    parser_spec.loader.exec_module(parser_module)
    IndianResumeParser = parser_module.IndianResumeParser
    logger.info("✅ Parser module loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load parser module: {e}")
    raise

# Load scorer module
try:
    scorer_spec = importlib.util.spec_from_file_location("ml.scorer", SCORER_PATH)
    scorer_module = importlib.util.module_from_spec(scorer_spec)
    scorer_spec.loader.exec_module(scorer_module)
    ATSScanner = scorer_module.ATSScanner
    logger.info("✅ Scorer module loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load scorer module: {e}")
    raise

# ============= OPTIONAL ML IMPORTS - GRACEFUL FAILURE =============
try:
    # Try to import ML modules - if they don't exist, app still works!
    from ml.ml_scorer import get_ml_scanner
    from ml.embeddings import get_embedding_model
    from ml.semantic_matcher import get_semantic_matcher
    ML_AVAILABLE = True
    logger.info("✅ ML modules loaded successfully (optional feature)")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"⚠️ ML modules not available: {e}")
    logger.info("   App continues with basic ATS scanning only")
    
    # Create placeholder functions
    def get_ml_scanner():
        return None
    def get_embedding_model():
        return None
    def get_semantic_matcher():
        return None

app = FastAPI(title="Indian ATS Resume Scanner API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
parser = IndianResumeParser()
scanner = ATSScanner()
logger.info("✅ Core components initialized")

# Initialize ML components only if available
if ML_AVAILABLE:
    try:
        ml_scanner = get_ml_scanner()
        embedding_model = get_embedding_model()
        semantic_matcher = get_semantic_matcher()
        logger.info("✅ ML components initialized")
    except Exception as e:
        logger.error(f"⚠️ ML initialization failed: {e}")
        ml_scanner = None
        embedding_model = None
        semantic_matcher = None
else:
    ml_scanner = None
    embedding_model = None
    semantic_matcher = None

# ============= EXISTING ENDPOINTS - WITH DEBUG LOGGING =============
@app.get("/")
def read_root():
    return {
        "message": "Indian ATS Resume Scanner API", 
        "status": "active",
        "ml_features": ML_AVAILABLE
    }

@app.post("/api/scan")
async def scan_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    job_title: Optional[str] = Form("")
):
    """
    Analyze resume against job description with debug logging
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] ===== SCAN REQUEST STARTED =====")
    logger.info(f"[{request_id}] File: {file.filename}")
    logger.info(f"[{request_id}] Job title: {job_title}")
    logger.info(f"[{request_id}] JD length: {len(job_description)}")
    
    try:
        # Save uploaded file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        logger.info(f"[{request_id}] File extension: {file_extension}")
        
        if file_extension not in ['pdf', 'docx']:
            logger.warning(f"[{request_id}] Unsupported file type: {file_extension}")
            return JSONResponse(
                status_code=400,
                content={"error": "Only PDF and DOCX files are supported"}
            )
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        logger.info(f"[{request_id}] Temp file created: {temp_file.name}")
        
        # Parse resume
        logger.info(f"[{request_id}] Extracting text from file...")
        text = parser.extract_text(temp_file.name, file_extension)
        logger.info(f"[{request_id}] Extracted text length: {len(text)}")
        
        logger.info(f"[{request_id}] Parsing resume...")
        resume_data = parser.parse_resume(text)
        logger.info(f"[{request_id}] Parsed - Sections: {list(resume_data.get('sections', {}).keys())}")
        logger.info(f"[{request_id}] Parsed - Skills: {len(resume_data.get('skills', []))}")
        logger.info(f"[{request_id}] Parsed - Experience: {len(resume_data.get('experience', []))}")
        
        # Clean up temp file
        os.unlink(temp_file.name)
        logger.info(f"[{request_id}] Temp file cleaned up")
        
        # Calculate ATS score
        if not job_description:
            job_description = "Looking for a skilled professional with relevant experience."
            logger.info(f"[{request_id}] Using default job description")
        
        logger.info(f"[{request_id}] Calculating ATS score...")
        ats_results = scanner.calculate_ats_score(resume_data, job_description)
        logger.info(f"[{request_id}] Score calculated: {ats_results.get('overall_score')}")
        
        # Prepare response
        response = {
            "resume_id": str(uuid.uuid4()),
            "file_name": file.filename,
            "parsed_data": {
                "skills": resume_data.get("skills", []),
                "experience": resume_data.get("experience", []),
                "sections_found": list(resume_data.get("sections", {}).keys()),
                "indian_info": resume_data.get("indian_specific", {})
            },
            "ats_analysis": ats_results,
            "recommendations": _generate_recommendations(ats_results, resume_data)
        }
        
        logger.info(f"[{request_id}] ===== SCAN REQUEST COMPLETED SUCCESSFULLY =====\n")
        return response
        
    except KeyError as e:
        logger.error(f"[{request_id}] ❌ KeyError: {str(e)}")
        logger.error(f"[{request_id}] Resume data keys: {resume_data.keys() if 'resume_data' in locals() else 'Not available'}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Missing key: {str(e)}")
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ Error processing resume: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/api/analyze-text")
async def analyze_resume_text(
    resume_text: str = Form(...),
    job_description: str = Form(...)
):
    """
    Analyze resume text directly with debug logging
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] ===== ANALYZE-TEXT REQUEST STARTED =====")
    logger.info(f"[{request_id}] Resume length: {len(resume_text)}")
    logger.info(f"[{request_id}] JD length: {len(job_description)}")
    logger.info(f"[{request_id}] Resume preview: {resume_text[:200]}...")
    logger.info(f"[{request_id}] JD preview: {job_description[:200]}...")
    
    try:
        # Validate inputs
        if not resume_text or len(resume_text.strip()) < 10:
            logger.warning(f"[{request_id}] Resume text is too short: {len(resume_text)}")
            raise HTTPException(status_code=400, detail="Resume text is too short")
        
        if not job_description or len(job_description.strip()) < 10:
            logger.warning(f"[{request_id}] Job description is too short: {len(job_description)}")
            raise HTTPException(status_code=400, detail="Job description is too short")
        
        # Parse resume from text
        logger.info(f"[{request_id}] Parsing resume text...")
        resume_data = parser.parse_resume(resume_text)
        logger.info(f"[{request_id}] Parsed - Sections: {list(resume_data.get('sections', {}).keys())}")
        logger.info(f"[{request_id}] Parsed - Skills: {len(resume_data.get('skills', []))}")
        logger.info(f"[{request_id}] Parsed - Experience: {len(resume_data.get('experience', []))}")
        logger.info(f"[{request_id}] Parsed - Education: {len(resume_data.get('education', []))}")
        
        # Calculate ATS score
        logger.info(f"[{request_id}] Calculating ATS score...")
        ats_results = scanner.calculate_ats_score(resume_data, job_description)
        logger.info(f"[{request_id}] Score calculated: {ats_results.get('overall_score')}")
        logger.info(f"[{request_id}] Component scores: {ats_results.get('component_scores', {})}")
        
        response = {
            "parsed_data": {
                "skills": resume_data.get("skills", []),
                "experience": resume_data.get("experience", []),
                "sections_found": list(resume_data.get("sections", {}).keys()),
                "indian_info": resume_data.get("indian_specific", {})
            },
            "ats_analysis": ats_results,
            "recommendations": _generate_recommendations(ats_results, resume_data)
        }
        
        logger.info(f"[{request_id}] ===== ANALYZE-TEXT REQUEST COMPLETED SUCCESSFULLY =====\n")
        return response
        
    except HTTPException:
        raise
        
    except KeyError as e:
        logger.error(f"[{request_id}] ❌ KeyError: {str(e)}")
        logger.error(f"[{request_id}] Resume data keys: {resume_data.keys() if 'resume_data' in locals() else 'Not available'}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Missing key: {str(e)}")
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ Error in analyze-text: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def _generate_recommendations(ats_results: Dict, resume_data: Dict) -> List[str]:
    """Generate specific recommendations"""
    recommendations = []
    
    # Based on missing keywords
    missing_keywords = ats_results.get("missing_keywords", [])
    if missing_keywords:
        recommendations.append(
            f"Add these keywords to your resume: {', '.join(missing_keywords[:5])}"
        )
    
    # Based on skills
    if len(resume_data.get("skills", [])) < 8:
        recommendations.append(
            "List at least 8-10 technical skills, starting with the most relevant"
        )
    
    # Format recommendations
    if ats_results.get("component_scores", {}).get("formatting", 1.0) < 0.8:
        recommendations.extend([
            "Use a simple, clean format without tables or columns",
            "Save as PDF to preserve formatting",
            "Use standard section headers (Experience, Education, Skills)"
        ])
    
    # Indian-specific recommendations
    indian_info = resume_data.get("indian_specific", {})
    if not indian_info.get("degrees"):
        recommendations.append(
            "Add your Indian educational qualifications (B.Tech, MCA, B.Sc, etc.)"
        )
    
    return recommendations[:5]

# ============= NEW OPTIONAL ML ENDPOINTS - ADDED, NOT REPLACED =============
@app.post("/api/ml/analyze")
async def ml_analyze_resume(
    resume_text: str = Form(...),
    job_description: str = Form(...)
):
    """
    OPTIONAL ML-powered analysis - Runs alongside your existing scanner
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] ===== ML ANALYZE REQUEST =====")
    
    # Check if ML is available
    if not ML_AVAILABLE or ml_scanner is None:
        logger.warning(f"[{request_id}] ML features not available")
        return {
            "ml_insights": None,
            "error": "ML features not installed",
            "note": "Your basic ATS scanner is still working perfectly",
            "install_instructions": "Run: pip install sentence-transformers torch"
        }
    
    try:
        # Parse resume using YOUR EXISTING parser (reuse, don't rewrite)
        resume_data = parser.parse_resume(resume_text)
        logger.info(f"[{request_id}] Parsed resume for ML - Skills: {len(resume_data.get('skills', []))}")
        
        # Extract skills from JD using simple method
        jd_skills = []
        jd_lower = job_description.lower()
        skill_categories = getattr(ml_scanner, 'skill_categories', {})
        for category, skills in skill_categories.items():
            if isinstance(skills, dict):
                skills_list = skills.get('skills', [])
            else:
                skills_list = skills
            for skill in skills_list:
                if isinstance(skill, str) and skill.lower() in jd_lower:
                    jd_skills.append(skill)
        
        logger.info(f"[{request_id}] Extracted {len(jd_skills)} skills from JD")
        
        # Get ML insights
        ml_insights = ml_scanner.get_ml_insights(
            resume_text=resume_text[:5000],  # Limit length
            job_text=job_description[:5000],
            resume_skills=resume_data.get("skills", [])
        )
        
        logger.info(f"[{request_id}] ML insights generated successfully")
        
        return {
            "ml_insights": ml_insights,
            "disclaimer": "These are experimental ML-powered insights. Your ATS score remains unchanged.",
            "parsed_skills": resume_data.get("skills", [])[:10],
            "ml_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ ML analysis error: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "ml_insights": None,
            "error": "ML analysis temporarily unavailable",
            "note": "Your basic ATS scanner is still working perfectly",
            "details": str(e)
        }

@app.post("/api/ml/semantic-similarity")
async def ml_semantic_similarity(
    text1: str = Form(...),
    text2: str = Form(...)
):
    """Calculate semantic similarity between two texts"""
    if not ML_AVAILABLE or embedding_model is None:
        return {
            "similarity": None,
            "error": "ML features not installed"
        }
    
    try:
        similarity = embedding_model.calculate_semantic_similarity(text1, text2)
        return {
            "similarity": round(similarity * 100, 2),
            "interpretation": _interpret_similarity(similarity)
        }
    except Exception as e:
        logger.error(f"Semantic similarity error: {e}")
        return {
            "similarity": None,
            "error": str(e)
        }

@app.get("/api/ml/status")
async def ml_status():
    """Check if ML features are available"""
    return {
        "ml_available": ML_AVAILABLE,
        "ml_scanner_ready": ml_scanner is not None if ML_AVAILABLE else False,
        "embedding_model_ready": embedding_model is not None if ML_AVAILABLE else False,
        "semantic_matcher_ready": semantic_matcher is not None if ML_AVAILABLE else False,
        "ml_version": "2.0.0" if ML_AVAILABLE else None,
        "note": "ML features are OPTIONAL add-ons. Core ATS scanner works without them.",
        "installation": "pip install sentence-transformers torch" if not ML_AVAILABLE else "Already installed"
    }

def _interpret_similarity(score: float) -> str:
    """Interpret semantic similarity score"""
    if score > 0.85:
        return "🎯 Excellent semantic match"
    elif score > 0.75:
        return "✅ Strong semantic alignment"
    elif score > 0.65:
        return "📈 Good semantic relevance"
    elif score > 0.5:
        return "📊 Moderate semantic match"
    elif score > 0.35:
        return "🔧 Low semantic similarity"
    else:
        return "⚠️ Very low semantic match"

# ============= HEALTH CHECK ENDPOINT =============
@app.get("/api/health")
async def health_check():
    """Complete health check of all systems"""
    return {
        "status": "healthy",
        "core_ats": {
            "parser": "loaded",
            "scanner": "loaded",
            "status": "operational"
        },
        "ml_features": {
            "available": ML_AVAILABLE,
            "ml_scanner": ml_scanner is not None if ML_AVAILABLE else False,
            "embedding_model": embedding_model is not None if ML_AVAILABLE else False,
            "semantic_matcher": semantic_matcher is not None if ML_AVAILABLE else False,
            "status": "operational" if ML_AVAILABLE and ml_scanner else "not_available",
            "message": "Optional feature - core ATS works without it"
        },
        "version": "2.1.0",
        "environment": "production"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Indian ATS Resume Scanner API v2.1")
    print(f"📁 Current directory: {current_dir}")
    print(f"✅ Core ATS Scanner: READY")
    print(f"📝 Debug logging: ENABLED")
    print(f"🤖 ML Features: {'AVAILABLE' if ML_AVAILABLE else 'NOT INSTALLED (optional)'}")
    if ML_AVAILABLE:
        print("   • ML Scanner: READY")
        print("   • Embedding Model: READY")
        print("   • Semantic Matcher: READY")
    else:
        print("   To enable ML features: pip install sentence-transformers torch")
    print("=" * 60)
    
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)