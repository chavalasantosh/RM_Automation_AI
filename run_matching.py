import os
import yaml
from src.document_processor import DocumentProcessor
from src.matching_engine import MatchingEngine
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('matching.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    logger = setup_logging()
    logger.info("Starting Resume Matching Engine...")
    
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded successfully")
    
    # Initialize components
    document_processor = DocumentProcessor()
    matching_engine = MatchingEngine(config=config)
    logger.info("Components initialized successfully")
    
    # Process job description
    job_file = "test_docs/jobs/ml_engineer_job.txt"
    logger.info(f"Processing job description: {job_file}")
    
    with open(job_file, 'r', encoding='utf-8') as f:
        job_description = f.read()
    
    # Process and match resumes
    resume_dir = "test_docs/profiles"
    for resume_file in os.listdir(resume_dir):
        if resume_file.endswith(('.txt', '.pdf', '.docx')):
            resume_path = os.path.join(resume_dir, resume_file)
            logger.info(f"\nProcessing resume: {resume_path}")
            
            try:
                # Process resume
                doc_result = document_processor.process_document(resume_path)
                if not doc_result or 'content' not in doc_result:
                    logger.warning(f"Could not process file {resume_file}")
                    continue
                
                # Match against job description
                match_result = matching_engine.match(job_description, doc_result['content'])
                
                # Print results
                print("\n" + "="*50)
                print(f"Resume: {resume_file}")
                print(f"Overall Match Score: {match_result['score']:.2%}")
                print("\nSection Scores:")
                for section, score in match_result['section_scores'].items():
                    print(f"  {section}: {score:.2%}")
                
                if match_result['missing_skills']:
                    print("\nMissing Skills:")
                    for skill in match_result['missing_skills']:
                        print(f"  ✗ {skill}")
                
                print("="*50 + "\n")
                
            except Exception as e:
                logger.error(f"Error processing {resume_file}: {str(e)}")
                continue
    
    logger.info("Processing completed")

if __name__ == "__main__":
    main() 