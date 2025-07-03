#!/usr/bin/env python3
"""
Resume Matching Engine CLI
A command-line interface for matching resumes against job descriptions.
"""

import os
import sys
import yaml
import logging
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import traceback

print("Starting CLI application...")

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
print(f"Adding src path: {src_path}")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    print("Attempting to import required modules...")
    from src.document_processor import DocumentProcessor
    from src.matching_engine import MatchingEngine
    from src.enhanced_document_processor import EnhancedDocumentProcessor
    print("Successfully imported all required modules")
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed and the src directory is properly set up.")
    sys.exit(1)

def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    print(f"Setting up logging with level: {log_level}")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"rme_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"Log file: {log_file}")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Also configure the document processor logger
    logging.getLogger('document_processor').setLevel(getattr(logging, log_level.upper()))
    print("Logging setup complete")

def load_config() -> dict:
    """Load configuration from config.yaml with fallback defaults."""
    print("Loading configuration...")
    default_config = {
        'document_processing': {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_formats': ['.txt', '.doc', '.docx', '.pdf']
        },
        'matching': {
            'threshold': 0.7,
            'weights': {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.15,
                'certifications': 0.15
            }
        }
    }
    
    try:
        config_path = Path('config.yaml')
        if config_path.exists():
            print(f"Found config file: {config_path}")
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults, keeping user values where provided
                config = {**default_config, **(user_config or {})}
                print("Configuration loaded successfully")
                return config
        else:
            print("config.yaml not found, using default configuration")
            return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration due to error")
        return default_config

def format_score(score: float) -> str:
    """Format a score as a percentage string."""
    return f"{score:.2%}"

def process_files(job_file: str, resume_files: List[str], threshold: float = 0.7) -> None:
    """Process job description and resume files."""
    print(f"\nProcessing files:")
    print(f"Job file: {job_file}")
    print(f"Resume files: {resume_files}")
    print(f"Threshold: {threshold}")
    
    try:
        # Initialize components with config
        print("\nInitializing components...")
        config = load_config()
        doc_processor = DocumentProcessor(config.get('document_processing', {}).get('max_file_size', 10 * 1024 * 1024))
        matching_engine = MatchingEngine(config)
        print("Components initialized successfully")
        
        # Process job description
        print(f"\nProcessing job description: {job_file}")
        job_result = doc_processor.process_document(job_file)
        if not job_result or 'content' not in job_result:
            print(f"Error: Could not process job description file: {job_file}")
            return
        
        job_content = job_result['content']
        print("Job description processed successfully")
        
        # Process and match each resume
        for resume_file in resume_files:
            print(f"\nProcessing resume: {resume_file}")
            try:
                # Process resume
                resume_result = doc_processor.process_document(resume_file)
                if not resume_result or 'content' not in resume_result:
                    print(f"Error: Could not process resume file: {resume_file}")
                    continue
                
                resume_content = resume_result['content']
                print("Resume processed successfully")
                
                # Match resume against job
                print("Matching resume against job description...")
                result = matching_engine.match(job_content, resume_content)
                
                if 'error' in result:
                    print(f"\nError matching resume: {result['error']}")
                    continue
                
                # Print results with better formatting
                print("\n" + "="*50)
                print(f"Resume: {os.path.basename(resume_file)}")
                
                # Overall score
                overall_score = result.get('score', 0.0)
                print(f"Overall Match Score: {format_score(overall_score)}")
                
                # Section scores
                section_scores = result.get('section_scores', {})
                if section_scores:
                    print("\nSection Scores:")
                    for section, score in section_scores.items():
                        print(f"  {section.title()}: {format_score(score)}")
                
                # Matching skills
                matching_skills = result.get('matching_skills', [])
                if matching_skills:
                    print("\nMatching Skills:")
                    for skill in sorted(matching_skills):
                        print(f"  ✓ {skill}")
                
                # Missing skills
                missing_skills = result.get('missing_skills', [])
                if missing_skills:
                    print("\nMissing Skills:")
                    for skill in sorted(missing_skills):
                        print(f"  ✗ {skill}")
                
                # Additional metadata if available
                if 'processed_at' in result:
                    print(f"\nProcessed at: {result['processed_at']}")
                
                print("="*50)
                
            except Exception as e:
                print(f"\nError processing resume {resume_file}: {str(e)}")
                print("Traceback:")
                print(traceback.format_exc())
                continue
                
    except Exception as e:
        print(f"\nError in process_files: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())

def main():
    """Main entry point for the CLI."""
    print("\nStarting main function...")
    parser = argparse.ArgumentParser(
        description="Resume Matching Engine CLI - Match resumes against job descriptions"
    )
    
    parser.add_argument(
        "job_file",
        help="Path to the job description file (PDF, DOCX, or TXT)"
    )
    
    parser.add_argument(
        "resume_files",
        nargs="+",
        help="Paths to one or more resume files (PDF, DOCX, or TXT)"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Matching threshold (0.0 to 1.0, default: 0.7)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    args = parser.parse_args()
    print(f"\nParsed arguments:")
    print(f"Job file: {args.job_file}")
    print(f"Resume files: {args.resume_files}")
    print(f"Threshold: {args.threshold}")
    print(f"Log level: {args.log_level}")
    
    # Validate threshold
    if not 0 <= args.threshold <= 1:
        print("Error: Threshold must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Validate files exist
    if not os.path.exists(args.job_file):
        print(f"Error: Job file not found: {args.job_file}")
        sys.exit(1)
    
    for resume_file in args.resume_files:
        if not os.path.exists(resume_file):
            print(f"Error: Resume file not found: {resume_file}")
            sys.exit(1)
    
    print("\nAll validations passed, starting file processing...")
    # Process files
    process_files(args.job_file, args.resume_files, args.threshold)
    print("\nFile processing completed")

if __name__ == "__main__":
    main() 