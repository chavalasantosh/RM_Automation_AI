# Resume Matching Engine (RME) - Comprehensive Documentation

## 1. Project Overview & Goals

The Resume Matching Engine (RME) is an advanced, AI-powered platform for matching candidate resumes to job descriptions. It leverages NLP, machine learning, and offline AI models to provide accurate, explainable, and customizable candidate-job matching. RME supports multiple document formats, batch processing, RESTful APIs, and a web interface for enterprise use.

**Key Goals:**
- Automate and enhance candidate-job matching
- Support multi-format document ingestion (TXT, PDF, DOCX, etc.)
- Provide explainable, section-wise, and skill-based scoring
- Enable both API and web-based workflows
- Allow easy extension and customization

---

## 2. System Architecture

**Main Components:**
- **Document Processor:** Extracts and cleans text from resumes and job descriptions (supports TXT, PDF, DOCX).
- **Enhanced Document Processor:** Adds advanced extraction (skills, experience, education) using regex and keyword search.
- **Matching Engine:** Computes similarity scores using transformer-based embeddings and section-wise analysis.
- **AI Models:** Uses Sentence Transformers and BERT for semantic matching (runs locally, no cloud dependency).
- **API Layer:** FastAPI-based RESTful interface for programmatic access.
- **Web Interface:** User-friendly dashboard for uploads, results, and analytics.
- **Database:** Stores users, jobs, matches, and feedback (SQLAlchemy, SQLite by default).
- **Visualization:** Generates skill/match analysis plots.

---

## 3. File & Directory Structure

- `src/` : Core logic (document processing, matching, skill registry)
- `app/` : API, web routes, authentication, database models
- `models/` : Pretrained NLP models (BERT, Sentence Transformers, etc.)
- `test_docs/` : Sample jobs and resumes for testing
- `uploads/` : Uploaded jobs and resumes (organized by type)
- `output/` : Generated reports and results
- `logs/` : Log files for debugging and audit
- `config.yaml` : Main configuration file
- `skills.yaml` : Skill definitions and categories
- `requirements.txt` : Python dependencies
- `main.py` : FastAPI server entry point
- `cli.py` : Command-line interface
- `run_matching.py` : Batch matching script
- `DOCUMENTATION.md`, `README.md`, `PROJECT_OVERVIEW.md` : Documentation

---

## 4. Installation & Setup

**Prerequisites:**
- Python 3.8+
- 8GB+ RAM (16GB recommended)
- 10GB+ free disk space
- (Optional) CUDA GPU for faster AI processing

**Steps:**
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd RME_Cursor
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download required models:
   ```bash
   python -m spacy download en_core_web_lg
   python scripts/download_models.py
   ```

---

## 5. Configuration

- Main config: `config.yaml`
- Skill categories: `skills.yaml`
- Environment variables (optional):
  ```bash
  export RME_CONFIG_PATH=/path/to/config.yaml
  export RME_MODEL_PATH=/path/to/models
  ```
- Adjust thresholds, weights, and allowed formats in `config.yaml` as needed.

---

## 6. Usage

### A. Command-Line (Batch Processing)
Run all resumes in `test_docs/profiles` against a job in `test_docs/jobs`:
```bash
python run_matching.py
```

### B. CLI (Single/Custom Match)
```bash
python cli.py <job_file> <resume1> <resume2> ...
```

### C. Web API
Start the server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
- API docs: [http://localhost:8001/docs](http://localhost:8001/docs)
- Example endpoint:
  - `POST /api/upload` (upload job and resumes)
  - `GET /api/matches` (list matches)

### D. Web Dashboard
- Access at [http://localhost:8001/](http://localhost:8001/)
- Upload jobs/resumes, view matches, analytics, and download reports

---

## 7. Core Logic

### A. Document Processing
- Extracts text from TXT, PDF, DOCX
- Cleans, splits, and sections content (skills, experience, education, etc.)
- Handles encoding, OCR (for PDFs), and metadata

### B. Matching Engine
- Uses Sentence Transformers for semantic similarity
- Section-wise scoring (skills, experience, education, certifications)
- Skill extraction and gap analysis
- Caching for fast repeated queries

### C. AI Models
- Local models: Sentence Transformers (`all-MiniLM-L6-v2`), BERT (`bert-base-uncased`)
- No cloud dependency; all inference is local
- Configurable model paths in `config.yaml`

---

## 8. Extending & Customizing

- **Add new skill categories:** Edit `skills.yaml`
- **Change matching weights/thresholds:** Edit `config.yaml`
- **Add new document formats:** Extend `DocumentProcessor` in `src/document_processor.py`
- **Integrate new models:** Update model loading in `src/matching_engine.py`
- **Add API endpoints:** Edit `app/routes/web.py` or `app/api/`

---

## 9. Troubleshooting

- **Missing Skills:** Update `skills.yaml` for your domain
- **File errors:** Check file format/encoding; try converting to TXT
- **Model errors:** Ensure models are present in `models/`
- **API not starting:** Check `uvicorn` install, port conflicts, firewall
- **Logs:** See `logs/` and `matching.log` for details

---

## 10. FAQ

- **Q: Can I use my own models?**
  - Yes, update model paths in `config.yaml` and ensure compatible interfaces.
- **Q: How do I add new job/resume files?**
  - Place them in `test_docs/jobs/` or `test_docs/profiles/`.
- **Q: Is there a web UI?**
  - Yes, run the server and access the dashboard at `/`.
- **Q: Can I export results?**
  - Yes, via the dashboard or API endpoints.

---

## 11. Contact & Support

- For questions, see `README.md`, `DOCUMENTATION.md`, or contact the maintainer.
- Issues and feature requests: open a GitHub issue.
- For enterprise support, contact the project owner directly. 