from src.matching_engine import MatchingEngine
from src.document_processor import DocumentProcessor
import json
import os

def extract_skills_from_text(text):
    """Extract skills from text by looking for sections after 'Skills:' or 'Required Skills:' or 'Preferred Skills:'"""
    skills = []
    lines = text.split('\n')
    capture = False
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith(('skills:', 'required skills:', 'preferred skills:')):
            capture = True
            continue
        if capture and line.startswith('-'):
            skill = line.strip('- ').strip()
            if skill:
                skills.append(skill)
        elif capture and not line.startswith('-') and line:
            capture = False
            
    return skills

def print_detailed_analysis(match):
    """Print detailed analysis of the match."""
    print("\n=== DETAILED MATCH ANALYSIS ===")
    
    # Overall Scores
    print("\nOverall Scores:")
    print(f"Total Match Score: {match['match_score']:.2%}")
    print(f"Skills Match: {match['matching_criteria']['skills_match']:.2%}")
    print(f"Experience Match: {match['matching_criteria']['experience_match']:.2%}")
    print(f"Certification Match: {match['matching_criteria']['certification_match']:.2%}")
    print(f"Availability Match: {match['matching_criteria']['availability_match']:.2%}")
    
    # Skills Analysis
    print("\nSkills Analysis:")
    print("\nMatching Required Skills:")
    for skill in match['detailed_analysis']['matching_required_skills']:
        print(f"✓ {skill}")
    
    print("\nMatching Preferred Skills:")
    for skill in match['detailed_analysis']['matching_preferred_skills']:
        print(f"✓ {skill}")
    
    print("\nMissing Required Skills:")
    for skill in match['detailed_analysis']['missing_required_skills']:
        print(f"✗ {skill}")
    
    print("\nMissing Preferred Skills:")
    for skill in match['detailed_analysis']['missing_preferred_skills']:
        print(f"✗ {skill}")
    
    # Experience Analysis
    print("\nExperience Analysis:")
    exp_analysis = match['detailed_analysis']['experience_analysis']
    print(f"Required Experience: {exp_analysis['required']} years")
    print(f"Available Experience: {exp_analysis['available']} years")
    
    # Certification Analysis
    print("\nCertification Analysis:")
    cert_analysis = match['detailed_analysis']['certification_analysis']
    if cert_analysis['matching']:
        print("Matching Certifications:")
        for cert in cert_analysis['matching']:
            print(f"✓ {cert}")
    else:
        print("No matching certifications found")

def main():
    # Initialize processors
    doc_processor = DocumentProcessor(upload_dir="test_docs")
    matching_engine = MatchingEngine()
    
    # Process Pavan's profile
    pavan_profile = doc_processor.process_document("test_docs/pavan_profile.txt")
    pavan_skills = extract_skills_from_text(pavan_profile['text'])
    
    # Process job description
    job_desc = doc_processor.process_document("test_docs/job_description.txt")
    required_skills = extract_skills_from_text(job_desc['text'])
    
    # Create resource and project objects
    resource = {
        'id': 'R001',
        'name': 'Pavan Kumar',
        'skills': pavan_skills,
        'experience': '5 years',
        'certifications': ['AWS Machine Learning Specialist', 'Google Cloud Professional Data Engineer', 'Deep Learning Specialization'],
        'bio': pavan_profile['text'],
        'availability': 12  # months
    }
    
    project = {
        'id': 'P001',
        'title': 'Senior Machine Learning Engineer',
        'description': job_desc['text'],
        'required_skills': required_skills,
        'preferred_skills': ['Natural Language Processing', 'Computer Vision', 'Docker', 'Git', 'MLOps'],
        'technical_requirements': '5+ years of experience in machine learning and deep learning',
        'duration': 12,  # months
        'preferred_certifications': ['AWS Machine Learning Specialist', 'Google Cloud Professional Data Engineer']
    }
    
    # Match resource with project
    matches = matching_engine.match_resources(project, [resource])
    
    # Print detailed analysis
    print_detailed_analysis(matches[0])

if __name__ == "__main__":
    main() 