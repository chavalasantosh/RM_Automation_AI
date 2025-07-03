# RME Quick Start Guide

This guide will help you get the Resume Matching Engine (RME) up and running quickly.

## 1. First-Time Setup

### Windows
```powershell
# 1. Install Python 3.8 or higher from python.org

# 2. Open PowerShell and navigate to project directory
cd path\to\RME

# 3. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install spaCy model
python -m spacy download en_core_web_sm
```

### Linux/Mac
```bash
# 1. Install Python 3.8 or higher
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.8 python3.8-venv

# 2. Navigate to project directory
cd path/to/RME

# 3. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install spaCy model
python -m spacy download en_core_web_sm
```

## 2. Verify Installation

Run this command to verify everything is set up correctly:
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Setup successful!')"
```

## 3. Quick Test Run

1. **Check Input Files**
   - Look in `jd/` directory for job descriptions
   - Look in `bench_profiles/` directory for candidate profiles
   - Ensure files are in correct JSON format

2. **Run the System**
   ```bash
   python main.py
   ```

3. **Check Output**
   - Look in `output/` directory
   - You should see multiple output files:
     - `match_results.pdf`
     - `match_results.docx`
     - `match_results.html`
     - `match_results.txt`

## 4. Common Tasks

### Adding a New Job Description
1. Create a new JSON file in `jd/` directory
2. Follow the format in the example below:
```json
{
    "title": "Job Title",
    "required_skills": ["skill1", "skill2"],
    "required_experience": 5,
    "required_certifications": ["cert1"],
    "preferred_skills": ["skill3"],
    "description": "Job description..."
}
```

### Adding a New Candidate Profile
1. Create a new JSON file in `bench_profiles/` directory
2. Follow the format in the example below:
```json
{
    "name": "Candidate Name",
    "skills": ["skill1", "skill2"],
    "years_of_experience": 5,
    "certifications": ["cert1"],
    "education": "Education Level",
    "availability": "full-time"
}
```

### Running a Single Match
```python
from src.matching_engine import MatchingEngine

# Load job and profile data
with open('jd/job.json', 'r') as f:
    job_data = json.load(f)
with open('bench_profiles/candidate.json', 'r') as f:
    profile_data = json.load(f)

# Run matching
engine = MatchingEngine()
result = engine.match(job_data, profile_data)
print(f"Match score: {result['match_score']*100}%")
```

## 5. Troubleshooting Quick Reference

### Common Issues and Solutions

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

2. **JSON format errors**
   - Validate JSON files using a JSON validator
   - Check for missing commas or brackets

3. **No output files generated**
   - Check `logs/app.log` for errors
   - Verify write permissions in `output/` directory

4. **Low match scores**
   - Review skill definitions in `skills.yaml`
   - Check for typos in job/candidate files
   - Verify skill names match exactly

## 6. Next Steps

1. Read the full documentation in `README.md`
2. Review the configuration in `config.yaml`
3. Check the skill definitions in `skills.yaml`
4. Run the test suite: `pytest`

## 7. Getting Help

- Check the logs in `logs/app.log`
- Review the full documentation
- Contact the development team
- Create an issue on GitHub

Remember: The full documentation in `README.md` contains detailed information about all aspects of the system. This quick-start guide is just to get you running quickly! 