import os
import sys
import logging
from pathlib import Path
import importlib
import yaml
import pytest
from typing import List, Dict, Any
import torch
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def verify_imports() -> bool:
    """Verify that all required modules can be imported."""
    required_modules = [
        "src.enhanced_document_processor",
        "src.ai_enhanced_matching",
        "src.ai_matching_integration",
        "src.matching_engine",
        "src.skill_categories",
        "main"
    ]
    
    logger.info("Verifying module imports...")
    for module in required_modules:
        try:
            importlib.import_module(module)
            logger.info(f"✓ Successfully imported {module}")
        except ImportError as e:
            logger.error(f"✗ Failed to import {module}: {e}")
            return False
    return True

def verify_models() -> bool:
    """Verify that all required AI models are present."""
    config = load_config()
    model_path = Path(config['ai']['model_path'])
    
    required_models = [
        model_path / "ai_models" / "sentence_transformer",
        model_path / "skill_models" / "codebert",
        model_path / "ai_models" / "experience"
    ]
    
    logger.info("Verifying AI models...")
    for model_dir in required_models:
        if not model_dir.exists():
            logger.error(f"✗ Model directory not found: {model_dir}")
            return False
        logger.info(f"✓ Found model directory: {model_dir}")
    return True

def verify_directories() -> bool:
    """Verify that all required directories exist."""
    required_dirs = [
        "logs",
        "data",
        "models",
        "temp_uploads",
        "test_docs",
        "templates"
    ]
    
    logger.info("Verifying directories...")
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            logger.error(f"✗ Directory not found: {dir_name}")
            return False
        logger.info(f"✓ Found directory: {dir_name}")
    return True

def verify_database() -> bool:
    """Verify database connection and schema."""
    try:
        from sqlalchemy import create_engine, inspect
        config = load_config()
        db_path = Path(config['database']['path'])
        
        if not db_path.exists():
            logger.error(f"✗ Database file not found: {db_path}")
            return False
            
        engine = create_engine(f"sqlite:///{db_path}")
        inspector = inspect(engine)
        
        required_tables = [
            "profiles",
            "job_descriptions",
            "matches",
            "skills"
        ]
        
        existing_tables = inspector.get_table_names()
        for table in required_tables:
            if table not in existing_tables:
                logger.error(f"✗ Required table not found: {table}")
                return False
            logger.info(f"✓ Found table: {table}")
            
        return True
    except Exception as e:
        logger.error(f"✗ Database verification failed: {e}")
        return False

def verify_api() -> bool:
    """Verify API endpoints using test client."""
    try:
        from main import app
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code != 200:
            logger.error("✗ Health endpoint failed")
            return False
        logger.info("✓ Health endpoint working")
        
        # Test API version
        config = load_config()
        if response.json()["version"] != config['api']['version']:
            logger.error("✗ API version mismatch")
            return False
        logger.info("✓ API version correct")
        
        return True
    except Exception as e:
        logger.error(f"✗ API verification failed: {e}")
        return False

def verify_document_processing() -> bool:
    """Verify document processing capabilities."""
    try:
        from src.enhanced_document_processor import EnhancedDocumentProcessor
        config = load_config()
        processor = EnhancedDocumentProcessor()
        
        # Create test files
        test_dir = Path("test_docs")
        test_dir.mkdir(exist_ok=True)
        
        # Test each supported format
        for format in config['document_processing']['supported_formats']:
            test_file = test_dir / f"test{format}"
            with open(test_file, "w") as f:
                f.write("Test content")
                
            try:
                result = processor.process_document(str(test_file))
                if result is None:
                    logger.error(f"✗ Failed to process {format}")
                    return False
                logger.info(f"✓ Successfully processed {format}")
            except Exception as e:
                logger.error(f"✗ Error processing {format}: {e}")
                return False
            finally:
                test_file.unlink()
                
        return True
    except Exception as e:
        logger.error(f"✗ Document processing verification failed: {e}")
        return False

def verify_ai_integration() -> bool:
    """Verify AI model integration."""
    try:
        from src.ai_matching_integration import AIMatchingIntegration
        config = load_config()
        ai_matcher = AIMatchingIntegration()
        
        # Test basic matching
        job_desc = "Python developer with 5 years experience"
        profile = "Experienced Python developer with machine learning skills"
        
        result = ai_matcher.match_with_ai_enhancement(job_desc, profile)
        if result is None:
            logger.error("✗ AI matching failed")
            return False
        logger.info("✓ AI matching working")
        
        # Verify CUDA availability if enabled
        if config['ai']['device'] == "cuda" and not torch.cuda.is_available():
            logger.error("✗ CUDA requested but not available")
            return False
        if torch.cuda.is_available():
            logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            
        return True
    except Exception as e:
        logger.error(f"✗ AI integration verification failed: {e}")
        return False

def run_tests() -> bool:
    """Run the test suite."""
    try:
        logger.info("Running test suite...")
        result = pytest.main(["-v", "tests/"])
        return result == 0
    except Exception as e:
        logger.error(f"✗ Test suite failed: {e}")
        return False

def main():
    """Run all verification steps."""
    logger.info("Starting integration verification...")
    
    checks = [
        ("Module imports", verify_imports),
        ("AI models", verify_models),
        ("Directories", verify_directories),
        ("Database", verify_database),
        ("API", verify_api),
        ("Document processing", verify_document_processing),
        ("AI integration", verify_ai_integration),
        ("Test suite", run_tests)
    ]
    
    all_passed = True
    for name, check in checks:
        logger.info(f"\nVerifying {name}...")
        if not check():
            logger.error(f"✗ {name} verification failed")
            all_passed = False
        else:
            logger.info(f"✓ {name} verification passed")
            
    if all_passed:
        logger.info("\n✓ All components verified successfully!")
        return 0
    else:
        logger.error("\n✗ Some verifications failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 