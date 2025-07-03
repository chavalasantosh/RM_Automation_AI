import os
import sys
import logging
from pathlib import Path
import shutil
import yaml
import sqlite3
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories() -> None:
    """Create all required directories."""
    directories = [
        "logs",
        "data",
        "models",
        "models/ai_models",
        "models/skill_models",
        "temp_uploads",
        "test_docs",
        "templates",
        "docs",
        "scripts",
        "uploads",
        "bench_profiles",
        "profiles",
        "jd",
        "jobs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def initialize_database() -> None:
    """Initialize SQLite database with required tables."""
    try:
        db_path = Path("data/rme.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                ai_analysis TEXT
            );
            
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            );
            
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                job_id INTEGER,
                score REAL NOT NULL,
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES profiles (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            );
            
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                level TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_profiles_filename ON profiles(filename);
            CREATE INDEX IF NOT EXISTS idx_jobs_title ON job_descriptions(title);
            CREATE INDEX IF NOT EXISTS idx_matches_score ON matches(score);
            CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

def create_template_files() -> None:
    """Create template files for reports and documentation."""
    templates = {
        "templates/report_template.docx": """
            This is a placeholder for the report template.
            Please replace this with an actual Word template.
        """,
        "docs/api.md": """
            # RME API Documentation
            
            ## Endpoints
            
            ### POST /match
            Match candidate profiles against a job description.
            
            ### POST /analyze
            Analyze a single profile with optional AI enhancement.
            
            ### GET /health
            Health check endpoint.
        """,
        "docs/matching_results.md": """
            # Matching Results Documentation
            
            ## Score Components
            
            - Skills match (40%)
            - Experience match (30%)
            - Education match (15%)
            - Certifications match (15%)
            
            ## AI Enhancement
            
            The system uses AI to enhance matching by:
            - Semantic skill matching
            - Experience context analysis
            - Role complexity matching
            - Industry-specific insights
        """
    }
    
    for path, content in templates.items():
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            logger.info(f"Created template file: {path}")

def create_log_files() -> None:
    """Create initial log files."""
    log_files = [
        "logs/rme.log",
        "logs/document_processor.log",
        "logs/ai_matching.log"
    ]
    
    for log_file in log_files:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            path.touch()
            logger.info(f"Created log file: {log_file}")

def verify_config() -> None:
    """Verify and update config.yaml if needed."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.error("config.yaml not found. Please create it first.")
        sys.exit(1)
        
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            
        # Verify required sections
        required_sections = [
            "app", "document_processing", "matching",
            "ai", "database", "api", "output",
            "testing", "logging", "security"
        ]
        
        for section in required_sections:
            if section not in config:
                logger.error(f"Missing required section in config.yaml: {section}")
                sys.exit(1)
                
        logger.info("Configuration verified successfully")
        
    except Exception as e:
        logger.error(f"Error verifying configuration: {e}")
        sys.exit(1)

def cleanup_temp_files() -> None:
    """Clean up any temporary files."""
    temp_dirs = ["temp_uploads", "test_docs"]
    
    for dir_name in temp_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            for file in dir_path.glob("*"):
                try:
                    if file.is_file():
                        file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete {file}: {e}")
                    
    logger.info("Temporary files cleaned up")

def main():
    """Run all setup steps."""
    try:
        logger.info("Starting project setup...")
        
        # Verify configuration first
        verify_config()
        
        # Create directory structure
        create_directories()
        
        # Initialize database
        initialize_database()
        
        # Create template files
        create_template_files()
        
        # Create log files
        create_log_files()
        
        # Clean up any temporary files
        cleanup_temp_files()
        
        logger.info("Project setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Run 'python scripts/download_models.py' to download AI models")
        logger.info("2. Run 'python scripts/verify_integration.py' to verify setup")
        logger.info("3. Start the server with 'python main.py'")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 