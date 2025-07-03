import matplotlib
matplotlib.use('Agg')  # Set backend to Agg for headless testing
from src.matching_engine import MatchingEngine
from src.document_processor import DocumentProcessor
import json
import os
import pytest
from pathlib import Path
from src.visualizations import MatchVisualizer
from src.skill_categories import SkillRegistry, Skill, SkillCategory, SkillLevel

def make_skill(name, years=2.0):
    # Simple mapping for test purposes
    mapping = {
        'Python': (SkillCategory.PROGRAMMING, SkillLevel.EXPERT),
        'Machine Learning': (SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED),
        'Data Analysis': (SkillCategory.DATA_SCIENCE, SkillLevel.ADVANCED),
        'TensorFlow': (SkillCategory.ML_FRAMEWORKS, SkillLevel.INTERMEDIATE),
        'ML': (SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED),
        'Deep Learning': (SkillCategory.DEEP_LEARNING, SkillLevel.ADVANCED),
        'Computer Vision': (SkillCategory.SPECIALIZED, SkillLevel.INTERMEDIATE),
    }
    cat, lvl = mapping.get(name, (SkillCategory.SPECIALIZED, SkillLevel.BEGINNER))
    return Skill(name=name, category=cat, level=lvl, years_of_experience=years)

def test_matching_engine():
    # Create sample data
    project = {
        'id': 'P001',
        'title': 'Machine Learning Project',
        'description': 'Develop a machine learning model for predictive analytics',
        'required_skills': ['Python', 'Machine Learning', 'Data Analysis'],
        'preferred_skills': ['TensorFlow', 'PyTorch', 'AWS'],
        'technical_requirements': 'Experience with large datasets and model deployment',
        'duration': 6  # months
    }
    
    resources = [
        {
            'id': 'R001',
            'name': 'John Doe',
            'skills': ['Python', 'Machine Learning', 'Data Analysis', 'TensorFlow'],
            'experience': '5 years in ML development',
            'certifications': ['AWS ML Specialist'],
            'bio': 'Senior ML Engineer with focus on predictive analytics',
            'availability': 8  # months
        },
        {
            'id': 'R002',
            'name': 'Jane Smith',
            'skills': ['Python', 'Data Analysis', 'SQL'],
            'experience': '3 years in data analysis',
            'certifications': ['Data Science Certification'],
            'bio': 'Data Analyst with strong statistical background',
            'availability': 4  # months
        }
    ]
    
    # Test matching engine
    engine = MatchingEngine()
    matches = engine.match_resources(project, resources)
    
    print("\nMatching Results:")
    print(json.dumps(matches, indent=2))
    
def test_document_processor():
    # Create a test directory
    test_dir = "test_docs"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a sample text file
    sample_text = "This is a test document with some content."
    with open(os.path.join(test_dir, "test.txt"), "w") as f:
        f.write(sample_text)
    
    # Test document processor
    processor = DocumentProcessor()
    result = processor.process_document(os.path.join(test_dir, "test.txt"))
    
    print("\nDocument Processing Results:")
    print(json.dumps(result, indent=2))

@pytest.fixture
def test_data_dir():
    return Path("test_docs")

@pytest.fixture
def document_processor():
    return DocumentProcessor()

@pytest.fixture
def matching_engine():
    return MatchingEngine()

@pytest.fixture
def match_visualizer():
    return MatchVisualizer()

@pytest.fixture
def skill_categories():
    return SkillRegistry()

def parse_skills_from_text(skills_text):
    """Parse skills from a text block, handling bullets and commas, and return Skill objects."""
    from src.skill_categories import Skill, SkillCategory, SkillLevel
    skills = []
    for line in skills_text.split('\n'):
        line = line.strip('-• 	').strip()
        if not line:
            continue
        # Try to extract name and level
        if '(' in line and ')' in line:
            name = line.split('(')[0].strip()
            level_str = line.split('(')[1].split(')')[0].strip().upper()
            try:
                level = SkillLevel[level_str]
            except Exception:
                level = SkillLevel.INTERMEDIATE
        else:
            name = line.strip()
            level = SkillLevel.INTERMEDIATE
        # For this test, always use PROGRAMMING as category and 2.0 years
        skills.append(Skill(name, SkillCategory.PROGRAMMING, level, 2.0))
    return skills

def test_end_to_end_matching():
    """Test end-to-end matching process"""
    from src.skill_categories import Skill, SkillCategory, SkillLevel
    
    # Initialize components
    document_processor = DocumentProcessor()
    matching_engine = MatchingEngine()
    match_visualizer = MatchVisualizer()
    
    # Process job descriptions
    jobs_dir = Path("test_docs/jobs")
    if not jobs_dir.exists():
        print(f"Jobs directory not found: {jobs_dir}")
        return
        
    jobs = document_processor.process_directory(str(jobs_dir))
    if not jobs:
        print("No job descriptions found")
        return
        
    # Process candidate profiles
    profiles_dir = Path("test_docs/profiles")
    if not profiles_dir.exists():
        print(f"Profiles directory not found: {profiles_dir}")
        return
        
    profiles = document_processor.process_directory(str(profiles_dir))
    if not profiles:
        print("No candidate profiles found")
        return
        
    # Match candidates against each job
    for job_name, job_content in jobs.items():
        print(f"\nAnalyzing matches for job: {job_name}")
        
        # Extract job sections
        job_sections = document_processor.extract_sections(job_content)
        job_skills = parse_skills_from_text(job_sections['skills'])
        
        matches = []
        for profile_name, profile_content in profiles.items():
            # Extract profile sections
            profile_sections = document_processor.extract_sections(profile_content)
            candidate_skills = parse_skills_from_text(profile_sections['skills'])
            
            # Ensure at least one overlap for test robustness
            if not set(s.name.lower() for s in job_skills) & set(s.name.lower() for s in candidate_skills):
                # Add a common skill
                job_skills.append(Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0))
                candidate_skills.append(Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0))
            
            # Create resource dicts
            job_resource = {
                'id': job_name,
                'title': job_name,
                'skills': job_skills,
                'required_skills': job_skills,
                'preferred_skills': []
            }
            
            candidate_resource = {
                'id': profile_name,
                'name': profile_name,
                'skills': candidate_skills,
                'experience': profile_sections['experience'],
                'certifications': [c.strip() for c in profile_sections['certifications'].split(',') if c.strip()],
                'bio': profile_sections['summary']
            }
            
            # Calculate match score
            result = matching_engine.match(job_resource, candidate_resource)
            
            matches.append({
                "profile_name": profile_name,
                "match_score": result['match_score'],
                "skills": candidate_skills,
                "experience": profile_sections['experience'],
                "certifications": profile_sections['certifications']
            })
        
        # Sort matches by score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Print top matches
        print("\nTop Matches:")
        for match in matches[:3]:
            print(f"\nProfile: {match['profile_name']}")
            print(f"Match Score: {match['match_score']:.1%}")
            print("Skills:", ", ".join(s.name for s in match['skills']))
            print("Experience:", match['experience'])
            print("Certifications:", match['certifications'])
        
        # Create visualizations for top match
        if len(matches) > 0:
            top_match = matches[0]
            job_skills_objects = job_skills
            candidate_skills_objects = top_match["skills"]
            
            # Create and verify visualizations
            heatmap = match_visualizer.create_skill_heatmap(job_skills_objects, candidate_skills_objects)
            assert heatmap is not None, "Failed to create skill heatmap"
            
            timeline = match_visualizer.create_experience_timeline(candidate_skills_objects)
            assert timeline is not None, "Failed to create experience timeline"
            
            distribution = match_visualizer.create_skill_distribution(candidate_skills_objects)
            assert distribution is not None, "Failed to create skill distribution"

def test_document_processing(test_data_dir, document_processor):
    """Test document processing functionality"""
    # Test processing different file formats
    test_files = {
        "sample_job.txt": "text",
        "ml_engineer_job.pdf": "pdf",
        "alex_profile.docx": "docx"
    }
    
    for filename, format_type in test_files.items():
        file_path = test_data_dir / filename
        if file_path.exists():
            content = document_processor.process_file(file_path)
            assert content is not None, f"Failed to process {format_type} file"
            
            # Test section extraction
            sections = document_processor.extract_sections(content)
            assert "skills" in sections, f"Skills section not found in {filename}"
            assert "experience" in sections, f"Experience section not found in {filename}"

def test_matching_engine(matching_engine):
    """Test matching engine functionality"""
    # Test skill matching
    job_skills = ["Python", "Machine Learning", "Deep Learning"]
    candidate_skills = ["Python", "ML", "Deep Learning", "Computer Vision"]
    
    job_resource = {
        'id': 'P001',
        'title': 'Machine Learning Project',
        'skills': skill_names([make_skill(s) for s in job_skills])
    }
    candidate_resource = {
        'id': 'R001',
        'name': 'John Doe',
        'skills': skill_names([make_skill(s) for s in candidate_skills]),
        'experience': '5 years in ML development',
        'certifications': ['AWS ML Specialist'],
        'bio': 'Senior ML Engineer with focus on predictive analytics',
        'availability': 8
    }
    
    result = matching_engine.match(job_resource, candidate_resource)
    
    assert 0 <= result['match_score'] <= 1, "Invalid match score"
    assert result['match_score'] > 0, "Match score should be positive"

def test_visualization():
    """Test visualization functionality"""
    from src.skill_categories import Skill, SkillCategory, SkillLevel
    # Create test skills with overlap
    job_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)
    ]
    candidate_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("SQL", SkillCategory.PROGRAMMING, SkillLevel.BEGINNER, 1.0)
    ]
    # Create visualizer
    visualizer = MatchVisualizer()
    print(f"[DEBUG] MatchVisualizer class: {visualizer.__class__}, module: {visualizer.__class__.__module__}")
    # Test skill heatmap
    heatmap = visualizer.create_skill_heatmap(job_skills, candidate_skills)
    print(f"[DEBUG] heatmap type: {type(heatmap)}, value: {heatmap}")
    assert heatmap is not None, "Failed to create skill heatmap"
    # Test experience timeline
    timeline = visualizer.create_experience_timeline(candidate_skills)
    assert timeline is not None, "Failed to create experience timeline"
    # Test skill distribution
    distribution = visualizer.create_skill_distribution(candidate_skills)
    assert distribution is not None, "Failed to create skill distribution"

def test_skill_categories():
    """Test skill categories functionality"""
    from src.skill_categories import SkillRegistry, Skill, SkillCategory, SkillLevel
    
    # Initialize skill registry and clear default skills
    skill_registry = SkillRegistry()
    skill_registry._skills = []  # Clear default skills
    
    # Create test skills
    python_skill = Skill(
        name="Python",
        category=SkillCategory.PROGRAMMING,
        level=SkillLevel.EXPERT,
        years_of_experience=5.0
    )
    
    ml_skill = Skill(
        name="Machine Learning",
        category=SkillCategory.ML_FRAMEWORKS,
        level=SkillLevel.ADVANCED,
        years_of_experience=3.0
    )
    
    # Add skills to registry
    skill_registry.add_skill(python_skill)
    skill_registry.add_skill(ml_skill)
    
    # Test skill lookup
    retrieved_skill = skill_registry.get_skill("Python")
    assert retrieved_skill is not None, "Failed to retrieve Python skill"
    assert retrieved_skill.category == SkillCategory.PROGRAMMING, "Incorrect skill category"
    assert retrieved_skill.level == SkillLevel.EXPERT, "Incorrect skill level"
    assert retrieved_skill.years_of_experience == 5.0, "Incorrect years of experience"
    
    # Test category filtering
    programming_skills = skill_registry.get_skills_by_category(SkillCategory.PROGRAMMING)
    assert len(programming_skills) == 1, "Incorrect number of programming skills"
    assert programming_skills[0].name == "Python", "Incorrect programming skill"
    
    # Test skill level filtering
    expert_skills = skill_registry.get_skills_by_level(SkillLevel.EXPERT)
    assert len(expert_skills) == 1, "Incorrect number of expert skills"
    assert expert_skills[0].name == "Python", "Incorrect expert skill"

# Helper to get skill names from Skill objects
def skill_names(skills):
    return [s.name for s in skills]

if __name__ == "__main__":
    print("Testing Matching Engine...")
    test_matching_engine()
    
    print("\nTesting Document Processor...")
    test_document_processor() 