import os
from datetime import datetime
from typing import Dict, List, Any
from src.document_processor import DocumentProcessor
from src.matching_engine import MatchingEngine
from src.visualizations import MatchVisualizer, Skill
from src.skill_categories import SkillRegistry, SkillCategory, SkillLevel
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def extract_skills_from_text(text: str, skill_registry: SkillRegistry) -> List[Skill]:
    """
    Extract skills from text using the skill registry.
    
    Args:
        text: Text to extract skills from
        skill_registry: SkillRegistry instance
        
    Returns:
        List of Skill objects
    """
    skills = []
    text_lower = text.lower()
    
    # Check each skill in the registry
    for skill in skill_registry.get_all_skills():
        if skill.name.lower() in text_lower:
            skills.append(skill)
    
    return skills

def extract_certifications_from_text(text: str) -> List[str]:
    """
    Extract certifications from text.
    
    Args:
        text: Text to extract certifications from
        
    Returns:
        List of certification names
    """
    certifications = []
    text_lower = text.lower()
    
    # Common certification keywords
    cert_keywords = ['certified', 'certification', 'certificate']
    
    # Split text into lines and look for certification mentions
    for line in text.split('\n'):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in cert_keywords):
            # Extract the certification name
            cert_name = line.strip()
            if cert_name:
                certifications.append(cert_name)
    
    return certifications

def create_radar_chart(match_data, candidate_name):
    """Create a radar chart for the match scores."""
    # Categories for the radar chart
    categories = ['Skills', 'Experience', 'Certifications', 'Availability']
    
    # Get the scores
    scores = [
        match_data['matching_criteria']['skills_match'],
        match_data['matching_criteria']['experience_match'],
        match_data['matching_criteria']['certification_match'],
        match_data['matching_criteria']['availability_match']
    ]
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Add the first value again to close the loop
    scores += scores[:1]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Plot data
    ax.plot(angles, scores, linewidth=2, linestyle='solid')
    ax.fill(angles, scores, alpha=0.25)
    
    # Set category labels
    plt.xticks(angles[:-1], categories)
    
    # Set y-axis limits
    ax.set_ylim(0, 1)
    
    # Add title
    plt.title(f'Match Analysis for {candidate_name}', size=15, y=1.1)
    
    # Save the plot
    plt.savefig(f'match_analysis_{candidate_name.lower().replace(" ", "_")}.png')
    plt.close()

def create_skill_comparison_chart(match_data, candidate_name):
    """Create a bar chart comparing required vs matching skills."""
    required_skills = set(match_data['detailed_analysis']['matching_required_skills'])
    preferred_skills = set(match_data['detailed_analysis']['matching_preferred_skills'])
    missing_required = set(match_data['detailed_analysis']['missing_required_skills'])
    missing_preferred = set(match_data['detailed_analysis']['missing_preferred_skills'])
    
    # Prepare data for plotting
    categories = ['Required Skills', 'Preferred Skills']
    matching = [len(required_skills), len(preferred_skills)]
    missing = [len(missing_required), len(missing_preferred)]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set width of bars
    barWidth = 0.35
    
    # Set positions of the bars
    r1 = np.arange(len(categories))
    r2 = [x + barWidth for x in r1]
    
    # Create bars
    ax.bar(r1, matching, width=barWidth, label='Matching Skills', color='green')
    ax.bar(r2, missing, width=barWidth, label='Missing Skills', color='red')
    
    # Add labels and title
    plt.xlabel('Skill Categories')
    plt.ylabel('Number of Skills')
    plt.title(f'Skill Match Analysis for {candidate_name}')
    plt.xticks([r + barWidth/2 for r in range(len(categories))], categories)
    plt.legend()
    
    # Save the plot
    plt.savefig(f'skill_analysis_{candidate_name.lower().replace(" ", "_")}.png')
    plt.close()

def print_detailed_analysis(candidate: Dict[str, Any], match_result: Dict[str, Any]):
    """Print detailed analysis of a candidate's match."""
    print(f"\n{'='*50}")
    print(f"CANDIDATE: {candidate['name']}")
    print(f"{'='*50}")
    
    # Overall match score
    print(f"\nMATCH SCORE: {match_result['match_score']*100:.1f}%")
    
    # Skills analysis
    print("\nSKILLS ANALYSIS:")
    print("-"*30)
    for category in SkillCategory:
        matching_skills = [s for s in candidate['skills'] if s.category == category]
        if matching_skills:
            print(f"\n{category.value}:")
            for skill in matching_skills:
                print(f"  • {skill.name} ({skill.level.value}) - {skill.years_of_experience:.1f} years")
    
    # Missing skills analysis
    if match_result.get('missing_skills'):
        print("\nMISSING SKILLS:")
        print("-"*30)
        for skill in match_result['missing_skills']:
            print(f"  • {skill}")
    
    # Experience analysis
    total_exp = sum(s.years_of_experience for s in candidate['skills'])
    avg_exp = total_exp / len(candidate['skills']) if candidate['skills'] else 0
    print(f"\nEXPERIENCE SUMMARY:")
    print("-"*30)
    print(f"  • Total Years: {total_exp:.1f}")
    print(f"  • Average Years per Skill: {avg_exp:.1f}")
    
    # Certifications
    if candidate.get('certifications'):
        print("\nCERTIFICATIONS:")
        print("-"*30)
        for cert in candidate['certifications']:
            print(f"  • {cert}")
    
    print("\n" + "="*50 + "\n")

def process_profile(profile_text: str, profile_name: str, skill_registry: SkillRegistry) -> Dict[str, Any]:
    """
    Process a profile text and extract relevant information.
    
    Args:
        profile_text: Text content of the profile
        profile_name: Name of the profile
        skill_registry: SkillRegistry instance
    
    Returns:
        Dictionary containing processed profile information
    """
    # Extract skills
    skills = extract_skills_from_text(profile_text, skill_registry)
    
    # Add years of experience based on skill level
    for skill in skills:
        if skill.level == SkillLevel.BEGINNER:
            skill.years_of_experience = 1.0
        elif skill.level == SkillLevel.INTERMEDIATE:
            skill.years_of_experience = 3.0
        elif skill.level == SkillLevel.ADVANCED:
            skill.years_of_experience = 5.0
        elif skill.level == SkillLevel.EXPERT:
            skill.years_of_experience = 8.0
    
    # Extract certifications
    certifications = extract_certifications_from_text(profile_text)
    
    # Create profile dictionary
    profile = {
        'id': profile_name,
        'name': profile_name,
        'skills': skills,
        'certifications': certifications,
        'years_of_experience': sum(skill.years_of_experience for skill in skills),
        'availability': 'Immediate'  # Default value
    }
    
    return profile

def main():
    """Main function to run the enhanced matching test."""
    # Initialize components
    doc_processor = DocumentProcessor()
    matching_engine = MatchingEngine()
    visualizer = MatchVisualizer()
    skill_registry = SkillRegistry()
    
    # Create test directories if they don't exist
    os.makedirs("test_docs/jobs", exist_ok=True)
    os.makedirs("test_docs/profiles", exist_ok=True)
    
    # Process job descriptions
    job_dir = "test_docs/jobs"
    jobs = doc_processor.process_directory(job_dir)
    
    if not jobs:
        print("No job descriptions found!")
        return
    
    # Process profiles
    profile_dir = "test_docs/profiles"
    profiles = {}
    
    # Process all profiles
    raw_profiles = doc_processor.process_directory(profile_dir)
    for profile_name, profile_text in raw_profiles.items():
        profiles[profile_name] = process_profile(profile_text, profile_name, skill_registry)
    
    if not profiles:
        print("No profiles found!")
        return
    
    # Match candidates against each job
    for job_name, job_text in jobs.items():
        print(f"\n{'='*50}")
        print(f"ANALYZING MATCHES FOR: {job_name.upper()}")
        print(f"{'='*50}\n")
        
        match_results = []
        
        for profile_name, profile in profiles.items():
            job_dict = {
                'title': job_name,
                'description': job_text,
                'required_skills': extract_skills_from_text(job_text, skill_registry),
                'preferred_skills': [],
                'technical_requirements': job_text,
                'skills': extract_skills_from_text(job_text, skill_registry)
            }
            match_result = matching_engine.match(candidate=profile, job=job_dict)
            match_result.update(profile)
            match_results.append(match_result)
            
            # Print detailed analysis
            print(f"\n{'='*50}")
            print(f"CANDIDATE: {profile_name.upper()}")
            print(f"{'='*50}")
            
            # Overall match score
            print(f"\nMATCH SCORE: {match_result['match_score']*100:.1f}%")
            
            # Skills analysis
            print("\nSKILLS ANALYSIS:")
            print("-"*30)
            for category in SkillCategory:
                matching_skills = [s for s in profile['skills'] if s.category == category]
                if matching_skills:
                    print(f"\n{category.value}:")
                    for skill in matching_skills:
                        print(f"  • {skill.name} ({skill.level.value}) - {skill.years_of_experience:.1f} years")
            
            # Missing skills analysis
            if match_result.get('missing_skills'):
                print("\nMISSING SKILLS:")
                print("-"*30)
                for skill in match_result['missing_skills']:
                    print(f"  • {skill}")
            
            # Experience analysis
            total_exp = sum(s.years_of_experience for s in profile['skills'])
            avg_exp = total_exp / len(profile['skills']) if profile['skills'] else 0
            print(f"\nEXPERIENCE SUMMARY:")
            print("-"*30)
            print(f"  • Total Years: {total_exp:.1f}")
            print(f"  • Average Years per Skill: {avg_exp:.1f}")
            
            # Certifications
            if profile.get('certifications'):
                print("\nCERTIFICATIONS:")
                print("-"*30)
                for cert in profile['certifications']:
                    print(f"  • {cert}")
            
            print("\n" + "="*50 + "\n")
            
            # Create visualizations
            visualizer.create_skill_heatmap(profile['skills'], f"Skill Heatmap - {profile_name}")
            visualizer.create_experience_timeline(profile['skills'], f"Experience Timeline - {profile_name}")
            if profile.get('certifications'):
                visualizer.create_certification_radar(profile['certifications'], f"Certification Radar - {profile_name}")
            visualizer.create_skill_gap_analysis(
                profile['skills'],
                match_result.get('missing_skills', []),
                f"Skill Gap Analysis - {profile_name}"
            )
        
        # Create comparison chart for this job
        visualizer.create_match_comparison(match_results, f"Candidate Comparison - {job_name}")
        
        # Sort and display top matches
        sorted_matches = sorted(match_results, key=lambda x: x['match_score'], reverse=True)
        print("\nTOP MATCHES:")
        print("-"*30)
        for i, match in enumerate(sorted_matches[:3], 1):
            print(f"{i}. {match['name']}: {match['match_score']*100:.1f}%")

if __name__ == "__main__":
    main() 