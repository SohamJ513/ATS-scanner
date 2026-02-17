"""
ML Models Directory - Placeholder for future trained models
This directory will contain fine-tuned models for Indian resumes
"""
import os

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(model_name: str) -> str:
    """Get path to a trained model file"""
    return os.path.join(MODELS_DIR, model_name)