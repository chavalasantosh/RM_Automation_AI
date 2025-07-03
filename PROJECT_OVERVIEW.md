# Resume Matching Engine (RME)

## Project Purpose & Features
The Resume Matching Engine (RME) is an AI-powered tool designed to match candidate resumes against job descriptions. It supports multiple document formats (TXT, PDF, DOCX), leverages advanced NLP models, and provides both a web API and command-line/script interfaces for flexible usage.

**Key Features:**
- Match resumes to job descriptions using AI and semantic similarity
- Supports TXT, PDF, and DOCX files
- Section-wise scoring (Skills, Experience, Education, Certifications)
- Identifies missing and matching skills
- CLI, script, and web API usage modes
- Configurable thresholds and skill categories
- Detailed logging and error handling

---

## How It Works (Overview)
1. **Document Processing:** Extracts and cleans text from resumes and job descriptions.
2. **Skill Extraction:** Identifies and categorizes skills using a configurable skill registry.
3. **Matching Engine:** Computes similarity scores between job requirements and candidate profiles using transformer-based embeddings.
4. **Result Reporting:** Outputs overall and section-wise match scores, and lists missing/matching skills.

---

## Usage Instructions

### 1. Direct Script Mode (Recommended for Batch Processing)
Run all resumes in `test_docs/profiles` against a job description in `test_docs/jobs`:
```sh
python run_matching.py
```
- Edit `run_matching.py` to change job or resume directories as needed.
- Results are printed to the console and logged in `matching.log`.

### 2. Command-Line Interface (CLI)
Match specific resumes to a job description:
```sh
python cli.py <job_file> <resume1> <resume2> ... [--log-level INFO]
```
Example:
```sh
python cli.py test_docs/jobs/ml_engineer_job.txt test_docs/profiles/ml_candidate.txt
```

### 3. Web API (FastAPI)
Start the server:
```sh
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- Access docs at: [http://localhost:8000/docs](http://localhost:8000/docs)
- Use `/match` endpoint to upload resumes and job descriptions

---

## Directory & File Structure
- `src/` : Core source code (document processing, matching engine, skill registry)
- `run_matching.py` : Batch script for matching all resumes
- `cli.py` : Command-line interface
- `main.py` : FastAPI web server
- `config.yaml` : Main configuration file
- `requirements.txt` : Python dependencies
- `models/` : Pretrained NLP models (required for matching)
- `test_docs/` : Sample job descriptions and resumes for testing
- `skills.yaml` : Skill definitions and categories
- `logs/` : Log files
- `output/` : Output files (if generated)
- `README.md`, `DOCUMENTATION.md`, `PROJECT_OVERVIEW.md` : Documentation

---

## Configuration
- All settings (paths, thresholds, logging, allowed file types) are in `config.yaml`.
- Skill categories and levels are defined in `skills.yaml`.

---

## Dependencies
Install all dependencies with:
```sh
pip install -r requirements.txt
```
Key packages:
- fastapi, uvicorn, python-docx, PyPDF2, sentence-transformers, scikit-learn, pandas, numpy, pyyaml, reportlab, matplotlib

---

## How to Add/Update Jobs & Resumes
- Place new job descriptions in `test_docs/jobs/` (TXT, PDF, or DOCX)
- Place new candidate resumes in `test_docs/profiles/` (TXT, PDF, or DOCX)
- Run the script or CLI as shown above

---

## Troubleshooting & FAQ
- **Missing Skills:** If all resumes show missing advanced skills, update `skills.yaml` to reflect your domain.
- **Corrupted Files:** If a file cannot be processed, check its format or try converting to TXT.
- **Model Errors:** Ensure all required models are present in the `models/` directory.
- **Web API Not Starting:** Make sure `uvicorn` is installed and not blocked by firewall.
- **Logs:** Check `logs/` and `matching.log` for detailed error messages.

---

## Contact/Support
For questions, contact the project maintainer or refer to the documentation files (`README.md`, `DOCUMENTATION.md`).

---

**This project is ready to be shared with senior engineers. All core files, configuration, and documentation are included.** 