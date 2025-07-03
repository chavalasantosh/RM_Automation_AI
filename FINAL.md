# Resume Matching Engine (RME) - Final Documentation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Directory Structure](#directory-structure)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage](#usage)
    - [Quick Start](#quick-start)
    - [Command-Line](#command-line)
    - [Web API](#web-api)
    - [Dashboard](#dashboard)
8. [API Documentation](#api-documentation)
9. [Sample Results & Analysis](#sample-results--analysis)
10. [Enhancements & Dashboard](#enhancements--dashboard)
11. [Troubleshooting & FAQ](#troubleshooting--faq)
12. [Contributing](#contributing)
13. [License](#license)
14. [Contact](#contact)
15. [Future Improvements & Roadmap](#future-improvements--roadmap)

---

## Project Overview

The Resume Matching Engine (RME) is an advanced, AI-powered platform for matching candidate resumes to job descriptions. It leverages NLP, machine learning, and offline AI models to provide accurate, explainable, and customizable candidate-job matching. RME supports multiple document formats, batch processing, RESTful APIs, and a web interface for enterprise use.

---

## Key Features
- Multi-format document processing (TXT, PDF, DOCX, etc.)
- AI-enhanced, semantic skill and experience matching
- Section-wise scoring (Skills, Experience, Education, Certifications)
- Skill gap analysis and recommendations
- Batch processing, CLI, API, and dashboard usage
- Configurable thresholds, skill categories, and weights
- Detailed logging, error handling, and reporting
- Local/offline AI model support (no cloud dependency)
- Modern, responsive frontend dashboard

---

## System Architecture
- **Document Processor:** Extracts and cleans text from resumes and job descriptions
- **Enhanced Document Processor:** Advanced extraction (skills, experience, education)
- **Matching Engine:** Computes similarity scores using transformer-based embeddings
- **AI Models:** Sentence Transformers, BERT (local inference)
- **API Layer:** FastAPI-based RESTful interface
- **Web Interface:** Dashboard for uploads, results, analytics
- **Database:** SQLAlchemy/SQLite (default)
- **Visualization:** Skill/match analysis plots, dashboards

---

## Directory Structure
```
RME_Cursor/
├── app/                # FastAPI app, API, routes, models
├── src/                # Core logic: document processing, matching
├── models/             # Pretrained NLP models
├── test_docs/          # Sample jobs and resumes
├── uploads/            # Uploaded jobs and resumes
├── output/             # Generated reports/results
├── logs/               # Log files
├── enhancements/       # Additional features (dashboard, reporting, etc.)
├── docs/               # Documentation, analysis, results
├── config.yaml         # Main configuration
├── skills.yaml         # Skill definitions/categories
├── requirements.txt    # Python dependencies
├── main.py             # FastAPI server entry point
├── cli.py              # Command-line interface
├── run_matching.py     # Batch matching script
└── ...
```

---

## Installation & Setup

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
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
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

## Configuration
- Main config: `config.yaml`
- Skill categories: `skills.yaml`
- Environment variables (optional):
  ```bash
  export RME_CONFIG_PATH=/path/to/config.yaml
  export RME_MODEL_PATH=/path/to/models
  ```
- Adjust thresholds, weights, and allowed formats in `config.yaml` as needed.

---

## Usage

### Quick Start
1. Place job descriptions in `jd/` and candidate profiles in `bench_profiles/` (JSON format)
2. Run:
   ```bash
   python main.py
   ```
3. Check output in `output/` directory (PDF, DOCX, HTML, TXT)

### Command-Line
- Batch process all resumes:
  ```bash
  python run_matching.py
  ```
- Match specific resumes to a job:
  ```bash
  python cli.py <job_file> <resume1> <resume2> ...
  ```

### Web API
- Start the server:
  ```bash
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- Access docs at: [http://localhost:8000/docs](http://localhost:8000/docs)
- Example endpoints:
  - `POST /match` (upload job and resumes)
  - `POST /analyze` (analyze a single profile)
  - `GET /health` (health check)

### Dashboard
- Run the dashboard:
  ```bash
  python enhancements/visualization/dashboard/run_dashboard.py
  ```
- Access at: [http://localhost:8501/](http://localhost:8501/)
- Visualize matches, skills, experience, and download reports

---

## API Documentation

### Endpoints
- **POST /match**: Match candidate profiles against a job description
- **POST /analyze**: Analyze a single profile with optional AI enhancement
- **GET /health**: Health check endpoint

#### Example: Match Profiles
```http
POST /match
Content-Type: multipart/form-data

Parameters:
- job_description: string
- files: file[] (multiple files)
- use_ai: boolean (default: true)
- threshold: float (default: 0.7)
```

#### Example: Analyze Profile
```http
POST /analyze
Content-Type: multipart/form-data
Parameters:
- file: file
- use_ai: boolean (default: true)
```

#### Example: Health Check
```http
GET /health
Response: { "status": "healthy", "version": "2.0.0", ... }
```

---

## Sample Results & Analysis

### Example Results
- **ML Engineer Job**
    - ml_candidate.txt: 80.0%
    - alex_profile.txt: 70.0%
    - priya_profile.txt: 70.0%
    - rahul_profile.txt: 35.0%
- **Sample Job**
    - alex_profile.txt: 67.9%
    - priya_profile.txt: 67.9%
    - ml_candidate.txt: 59.3%
    - rahul_profile.txt: 42.1%

#### Candidate Comparison Matrix
| Candidate         | Match Score | Key Skills                  | Experience | Certifications      |
|------------------|-------------|-----------------------------|------------|--------------------|
| ml_candidate.txt | 80.0%       | TensorFlow, PyTorch, DL     | 49.0 years | None               |
| alex_profile.txt | 70.0%       | TensorFlow, PyTorch, K8s    | 48.0 years | None               |
| priya_profile.txt| 70.0%       | PyTorch, Deep Learning, CUDA| 52.0 years | NVIDIA DL          |
| rahul_profile.txt| 35.0%       | Scikit-learn, Data Science  | 26.0 years | Data Science, SQL  |

#### Visualizations
- Pie charts, skill matrices, and experience graphs are available in the dashboard and reports.

---

## Enhancements & Dashboard
- **Excel & PowerPoint Reports**: Generate detailed analysis and executive summaries
- **Interactive Dashboard**: Streamlit-based, real-time data visualization, filtering, and export
- **Skill Matrices & Timelines**: Visualize skill gaps, experience, and certification coverage
- **Advanced Matching**: ML-based skill similarity, industry-specific rules, and custom templates
- **User Interface**: Drag-and-drop upload, progress tracking, real-time preview

---

## Troubleshooting & FAQ
- **Missing Skills**: Update `skills.yaml` for your domain
- **File errors**: Check file format/encoding; try converting to TXT
- **Model errors**: Ensure models are present in `models/`
- **API not starting**: Check `uvicorn` install, port conflicts, firewall
- **Logs**: See `logs/` and `matching.log` for details
- **Low match scores**: Review skill definitions and input file formats

---

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contact
For questions, see `README.md`, `DOCUMENTATION.md`, or contact the maintainer. For enterprise support, contact the project owner directly.

---

## Future Improvements & Roadmap

### 🧠 AI/ML Improvements
- **Explainable AI**: Integrate SHAP, LIME, or attention heatmaps to justify each score and provide transparency in candidate-job matching.
- **Natural Language Query Interface**: Add a chatbot or prompt-based interface to allow users to interact with results using natural language.
- **Multilingual Support**: Implement language detection and support for processing resumes and job descriptions in multiple languages.
- **Custom Embeddings**: Allow users to load their own `.pt` or `.onnx` embedding models for domain-specific similarity and matching.

### 📊 Dashboard & Visualization
- **Dynamic Filters**: Enable filtering of results by match range, skill clusters, candidate names, and more.
- **Export Options**: Provide one-click export to Excel, PDF, and PNG directly from the dashboard.
- **Real-Time Matching UI**: Use WebSockets or background polling to display score progress and updates in real time.
- **Keyword Cloud**: Visualize the most frequent or matched terms using keyword clouds.
- **Experience Timeline Visualization**: Graphically display candidate experience across years in the dashboard.

### 📦 Package & Distribution
- **PyPI/Installable CLI Tool**: Package the CLI as an installable Python package (with `setup.py` and `entry_points`) for easy distribution.
- **Unit Tests & CI**: Integrate `pytest` and continuous integration (e.g., GitHub Actions, GitLab CI) to run tests on every push.
- **Model Registry**: Maintain a registry or versioning system for models, especially for fine-tuned or custom models.
- **i18n**: Internationalize the UI to support multiple locales and languages.

### 📁 Docs & Developer Experience
- **README.md with Shields**: Add badges for build status, license, coverage, etc., to the README.
- **Design Docs**: Create `docs/design_architecture.md` or an `ADR/` folder to document architectural and design decisions.

### 📉 Result Optimization & Matching Logic
- **Feedback Loop**: Add an optional user feedback input (e.g., "Was this match useful?") to help fine-tune future scoring.
- **Weight Tuning Interface**: Provide a UI to tweak `config.yaml` weights and see real-time impact on results.
- **Skill Synonyms**: Implement a synonym mapper to handle equivalent skills (e.g., "Kubernetes" vs "K8s").
- **Matching Explanation Report**: Generate a PDF for each candidate explaining "Why this score?" with detailed breakdowns.

### 📊 Advanced Use-Cases (Enterprise)
- **JD Generator**: Automatically generate job descriptions from top-performing resumes.
- **Resume Enhancer**: Suggest areas for candidate improvement based on job requirements.
- **Domain-Based Matching Templates**: Support different matching configurations for tech, finance, sales, and other domains. 