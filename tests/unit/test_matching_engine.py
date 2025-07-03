import pytest
from src.matching_engine import MatchingEngine
from typing import Dict, Any
from src.skill_categories import Skill, SkillCategory, SkillLevel

def test_match_candidate_basic(mock_matching_engine, sample_profile, sample_job):
    """Test basic candidate matching."""
    score = mock_matching_engine.match_candidate(sample_profile, sample_job)
    assert 0 <= score <= 1
    assert isinstance(score, float)

def test_match_candidate_perfect_match():
    """Test matching a candidate with perfect skills match"""
    # Create sample job and profile
    job_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)
    ]
    
    candidate_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)
    ]
    
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': []
    }
    
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '5 years in ML',
        'certifications': ['AWS ML Specialty'],
        'bio': 'Experienced ML engineer'
    }
    
    # Test matching
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    
    # Perfect match should have a high score
    assert result['match_score'] >= 0.6, f"Expected high match score, got {result['match_score']}"

def test_match_candidate_no_match():
    """Test matching a candidate with no overlapping skills"""
    job_skills = [Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    candidate_skills = [Skill("Java", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': []
    }
    
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '5 years in software',
        'certifications': [],
        'bio': 'Experienced software engineer'
    }
    
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert result['match_score'] == 0.0, f"Expected 0.0 match score, got {result['match_score']}"

def test_match_candidate_partial_match():
    """Test matching a candidate with partial skill overlap"""
    job_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)
    ]
    candidate_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Java", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)
    ]
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': []
    }
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '5 years in software',
        'certifications': [],
        'bio': 'Experienced software engineer'
    }
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert 0.0 < result['match_score'] < 1.0, f"Expected partial match score, got {result['match_score']}"

def test_match_candidate_skill_levels():
    """Test matching a candidate with different skill levels"""
    job_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.INTERMEDIATE, 3.0)
    ]
    candidate_skills = [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.INTERMEDIATE, 3.0),
        Skill("Machine Learning", SkillCategory.PROGRAMMING, SkillLevel.INTERMEDIATE, 3.0)
    ]
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': []
    }
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '3 years in software',
        'certifications': [],
        'bio': 'Intermediate software engineer'
    }
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert 0.0 < result['match_score'] < 1.0, f"Expected partial match score, got {result['match_score']}"

def test_match_candidate_certifications():
    """Test matching a candidate with matching certifications"""
    job_skills = [Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    candidate_skills = [Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': [],
        'certifications': ['AWS ML Specialty']
    }
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '5 years in software',
        'certifications': ['AWS ML Specialty'],
        'bio': 'Certified ML engineer'
    }
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert result['match_score'] > 0.0, f"Expected positive match score, got {result['match_score']}"

def test_match_candidate_experience():
    """Test matching a candidate with matching experience"""
    job_skills = [Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    candidate_skills = [Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0)]
    job_resource = {
        'id': 'test_job',
        'title': 'ML Engineer',
        'skills': job_skills,
        'required_skills': job_skills,
        'preferred_skills': [],
        'experience': '5 years'
    }
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Test Candidate',
        'skills': candidate_skills,
        'experience': '5 years',
        'certifications': [],
        'bio': 'Experienced engineer'
    }
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert result['match_score'] > 0.0, f"Expected positive match score, got {result['match_score']}"

def test_match_candidate_empty_inputs():
    """Test matching with empty inputs"""
    job_resource = {
        'id': 'test_job',
        'title': 'Empty Job',
        'skills': [],
        'required_skills': [],
        'preferred_skills': []
    }
    candidate_resource = {
        'id': 'test_candidate',
        'name': 'Empty Candidate',
        'skills': [],
        'experience': '',
        'certifications': [],
        'bio': ''
    }
    matching_engine = MatchingEngine()
    result = matching_engine.match(job_resource, candidate_resource)
    assert result['match_score'] == 0.0, f"Expected 0.0 match score for empty inputs, got {result['match_score']}"

def test_match_candidate_invalid_inputs():
    """Test matching with invalid inputs"""
    matching_engine = MatchingEngine()
    with pytest.raises(Exception):
        matching_engine.match(None, None)
    with pytest.raises(Exception):
        matching_engine.match({}, {})
    with pytest.raises(Exception):
        matching_engine.match({'skills': None}, {'skills': None})

def test_match_candidate_missing_fields():
    """Test matching with missing fields."""
    profile = {"skills": []}
    job = {"skills": []}
    engine = MatchingEngine()
    with pytest.raises(ValueError):
        engine.match_candidate(profile, job) 