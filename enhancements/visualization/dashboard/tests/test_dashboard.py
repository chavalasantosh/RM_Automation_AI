"""
Test cases for the RME Dashboard.
"""

import pytest
import pandas as pd
import json
import os
from pathlib import Path
from ..app import (
    load_match_results,
    create_match_summary_df,
    create_skill_matrix_df,
    create_experience_timeline_df
)

@pytest.fixture
def sample_results():
    """Create sample match results for testing."""
    return [
        {
            'job': 'Software Engineer',
            'profile': 'John Doe',
            'match_score': 85,
            'matching_criteria': {
                'experience_match': 90,
                'certification_match': 80,
                'availability_match': 85
            },
            'job_data': {
                'required_skills': ['Python', 'Java', 'SQL'],
                'education': 'Bachelor\'s',
                'years_experience': 3
            },
            'profile_data': {
                'skills': ['Python', 'Java', 'JavaScript'],
                'education': 'Bachelor\'s',
                'years_of_experience': 4,
                'certifications': ['AWS', 'Python']
            }
        },
        {
            'job': 'Data Scientist',
            'profile': 'Jane Smith',
            'match_score': 75,
            'matching_criteria': {
                'experience_match': 70,
                'certification_match': 80,
                'availability_match': 75
            },
            'job_data': {
                'required_skills': ['Python', 'R', 'Machine Learning'],
                'education': 'Master\'s',
                'years_experience': 2
            },
            'profile_data': {
                'skills': ['Python', 'R', 'SQL'],
                'education': 'Master\'s',
                'years_of_experience': 3,
                'certifications': ['Data Science', 'Python']
            }
        }
    ]

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory with sample results."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Save sample results
    for i, result in enumerate(sample_results()):
        with open(output_dir / f"match_{i}.json", 'w') as f:
            json.dump(result, f)
    
    return output_dir

def test_load_match_results(temp_output_dir):
    """Test loading match results from JSON files."""
    results = load_match_results(str(temp_output_dir))
    assert len(results) == 2
    assert results[0]['job'] == 'Software Engineer'
    assert results[1]['profile'] == 'Jane Smith'

def test_create_match_summary_df(sample_results):
    """Test creating summary DataFrame."""
    df = create_match_summary_df(sample_results)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'Match Score' in df.columns
    assert df['Match Score'].max() == 85
    assert df['Match Score'].min() == 75

def test_create_skill_matrix_df(sample_results):
    """Test creating skill matrix DataFrame."""
    df = create_skill_matrix_df(sample_results)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'Required Skills' in df.columns
    assert 'Matching Skills' in df.columns
    assert 'Missing Skills' in df.columns
    
    # Check skill matching
    se_match = df[df['Job'] == 'Software Engineer'].iloc[0]
    assert 'Python' in se_match['Matching Skills']
    assert 'SQL' in se_match['Missing Skills']

def test_create_experience_timeline_df(sample_results):
    """Test creating experience timeline DataFrame."""
    df = create_experience_timeline_df(sample_results)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'Experience (Years)' in df.columns
    assert 'Education' in df.columns
    assert df['Experience (Years)'].max() == 4
    assert df['Experience (Years)'].min() == 3

def test_dashboard_integration(temp_output_dir):
    """Test dashboard integration with Excel export."""
    from ..excel_generator import ExcelReport
    
    # Load results
    results = load_match_results(str(temp_output_dir))
    
    # Create Excel report
    report = ExcelReport(results)
    output_file = report.generate()
    
    # Verify report was created
    assert os.path.exists(output_file)
    assert output_file.endswith('.xlsx')
    
    # Clean up
    os.remove(output_file)

def test_data_consistency(sample_results):
    """Test data consistency across different views."""
    # Create all DataFrames
    summary_df = create_match_summary_df(sample_results)
    skill_df = create_skill_matrix_df(sample_results)
    exp_df = create_experience_timeline_df(sample_results)
    
    # Check job-profile pairs are consistent
    summary_pairs = set(zip(summary_df['Job'], summary_df['Candidate']))
    skill_pairs = set(zip(skill_df['Job'], skill_df['Candidate']))
    exp_pairs = set(zip(exp_df['Candidate'], exp_df['Candidate']))  # Only candidates in exp_df
    
    assert summary_pairs == skill_pairs
    assert all(candidate in exp_df['Candidate'].values for _, candidate in summary_pairs)
    
    # Check match scores are consistent
    for _, row in summary_df.iterrows():
        job, candidate = row['Job'], row['Candidate']
        skill_score = skill_df[
            (skill_df['Job'] == job) & 
            (skill_df['Candidate'] == candidate)
        ]['Match Score'].iloc[0]
        assert row['Match Score'] == skill_score

def test_error_handling():
    """Test error handling for invalid data."""
    # Test with empty results
    empty_df = create_match_summary_df([])
    assert len(empty_df) == 0
    
    # Test with missing data
    invalid_results = [{
        'job': 'Test Job',
        'profile': 'Test Profile',
        'match_score': 50
        # Missing matching_criteria and other fields
    }]
    
    # Should handle missing data gracefully
    df = create_match_summary_df(invalid_results)
    assert len(df) == 1
    assert pd.isna(df['Experience Match'].iloc[0])
    assert pd.isna(df['Certification Match'].iloc[0]) 