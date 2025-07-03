import os
import sys
import logging
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import spacy
import yaml
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def check_model_exists(model_path: Path, model_type: str) -> bool:
    """
    Check if a model exists and is valid.
    
    Args:
        model_path: Path to the model directory
        model_type: Type of model ('spacy', 'sentence_transformer', 'skill_model', 'experience_model')
        
    Returns:
        bool: True if model exists and is valid, False otherwise
    """
    try:
        if model_type == 'spacy':
            # Try to load the spaCy model directly
            try:
                spacy.load("en_core_web_lg")
                return True
            except OSError:
                return False
        elif model_type == 'sentence_transformer':
            # Check if sentence transformer model files exist
            if not model_path.exists():
                return False
            required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
            return all((model_path / f).exists() for f in required_files)
        elif model_type in ['skill_model', 'experience_model']:
            # Check if transformer model files exist
            if not model_path.exists():
                return False
            required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
            return all((model_path / f).exists() for f in required_files)
        return False
    except Exception as e:
        logger.warning(f"Error checking {model_type} model: {e}")
        return False

def download_file(url: str, dest_path: Path, chunk_size: int = 8192):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as f, tqdm(
        desc=dest_path.name,
        total=total_size,
        unit='iB',
        unit_scale=True
    ) as pbar:
        for data in response.iter_content(chunk_size=chunk_size):
            size = f.write(data)
            pbar.update(size)

def setup_models():
    """Download and set up required AI models only if they don't exist."""
    config = load_config()
    model_path = Path(config['ai']['model_path'])
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (model_path / "skill_models").mkdir(exist_ok=True)
    (model_path / "ai_models").mkdir(exist_ok=True)
    
    logger.info("Checking AI models...")
    
    # Check and download spaCy model
    if not check_model_exists(None, 'spacy'):
        logger.info("Downloading spaCy model...")
        try:
            spacy.cli.download("en_core_web_lg")
            logger.info("✓ SpaCy model downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading spaCy model: {e}")
            sys.exit(1)
    else:
        logger.info("✓ SpaCy model already exists")
        
    # Check and download sentence transformer model
    sentence_model_path = model_path / "ai_models" / "sentence_transformer"
    if not check_model_exists(sentence_model_path, 'sentence_transformer'):
        logger.info("Downloading sentence transformer model...")
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            model.save(str(sentence_model_path))
            logger.info("✓ Sentence transformer model downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading sentence transformer model: {e}")
            sys.exit(1)
    else:
        logger.info("✓ Sentence transformer model already exists")
        
    # Check and download skill model
    skill_model_path = model_path / "skill_models" / "codebert"
    if not check_model_exists(skill_model_path, 'skill_model'):
        logger.info("Downloading skill model...")
        try:
            skill_model = AutoModel.from_pretrained('microsoft/codebert-base')
            skill_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
            
            skill_model.save_pretrained(str(skill_model_path))
            skill_tokenizer.save_pretrained(str(skill_model_path))
            logger.info("✓ Skill model downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading skill model: {e}")
            sys.exit(1)
    else:
        logger.info("✓ Skill model already exists")
        
    # Check and download experience analysis model
    exp_model_path = model_path / "ai_models" / "experience"
    if not check_model_exists(exp_model_path, 'experience_model'):
        logger.info("Downloading experience analysis model...")
        try:
            exp_model = AutoModel.from_pretrained('distilbert-base-uncased')
            exp_tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
            
            exp_model.save_pretrained(str(exp_model_path))
            exp_tokenizer.save_pretrained(str(exp_model_path))
            logger.info("✓ Experience model downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading experience model: {e}")
            sys.exit(1)
    else:
        logger.info("✓ Experience model already exists")
        
    # Verify CUDA availability
    if torch.cuda.is_available():
        logger.info(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("CUDA is not available. Using CPU for inference.")

if __name__ == "__main__":
    try:
        setup_models()
        logger.info("Model setup completed successfully!")
    except Exception as e:
        logger.error(f"Error during model setup: {e}")
        sys.exit(1) 