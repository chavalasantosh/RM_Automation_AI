# Advanced Resume Matching Engine (RME) with AI Enhancement

## Overview
The Resume Matching Engine (RME) is an advanced system designed for matching candidate profiles with job descriptions using NLP, machine learning, and AI capabilities. The system now includes offline AI enhancement using open-source models for improved matching accuracy and deeper analysis.

## Key Features

### Enhanced Document Processing
- Support for multiple document formats:
  - Text files (.txt)
  - Word documents (.doc, .docx)
  - PDF files (.pdf)
  - Excel spreadsheets (.xlsx, .xls)
  - CSV files (.csv)
  - HTML files (.html, .htm)
  - Markdown files (.md)
  - JSON files (.json)
  - YAML files (.yaml, .yml)
  - OpenDocument formats (.odt, .ods, .odp)
  - RTF files (.rtf)
- Automatic encoding detection
- OCR support for PDF files
- Section extraction and categorization
- Metadata extraction

### AI-Enhanced Matching
- Offline AI capabilities using open-source models
- Advanced skill matching with semantic understanding
- Experience context analysis
- Role complexity matching
- Industry-specific insights
- Detailed skill gap analysis
- AI-powered recommendations
- Local model support (no cloud dependencies)

### Core Features
- Multi-format document processing
- Advanced matching algorithms
- Skill categorization and leveling
- Experience analysis
- Education verification
- Certification tracking
- Customizable matching criteria
- Batch processing support
- Detailed matching reports
- RESTful API interface

## System Architecture

### Components
1. **Enhanced Document Processor**
   - Handles multiple document formats
   - Extracts text and metadata
   - Performs OCR when needed
   - Categorizes content sections

2. **AI Matching Integration**
   - Integrates offline AI models
   - Provides semantic analysis
   - Enhances matching accuracy
   - Generates detailed insights

3. **Matching Engine**
   - Core matching algorithms
   - Score calculation
   - Threshold-based filtering
   - Result ranking

4. **API Layer**
   - FastAPI-based REST interface
   - Async request handling
   - File upload support
   - JSON response formatting

## Prerequisites

### System Requirements
   - Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space
- CUDA-capable GPU (optional, for faster AI processing)

### Python Dependencies
See `requirements.txt` for complete list, including:
- Core dependencies (FastAPI, uvicorn)
- Document processing (pdfplumber, python-docx)
- NLP and ML (spacy, transformers)
- AI models (torch, sentence-transformers)
- Data processing (pandas, numpy)
- Testing (pytest)

## Installation

1. Clone the repository:
   ```bash
git clone https://github.com/yourusername/rme.git
cd rme
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
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

## Configuration

1. Create a `config.yaml` file:
```yaml
app:
  host: "0.0.0.0"
  port: 8000
  debug: false

matching:
  threshold: 0.7
  use_ai: true
  batch_size: 10

ai:
  model_path: "models"
  device: "auto"  # or "cuda" or "cpu"
  batch_size: 8

document_processing:
  max_file_size: 10485760  # 10MB
  supported_formats:
    - .txt
    - .docx
    - .pdf
    - .xlsx
    - .csv
    - .html
    - .md
    - .json
    - .yaml
```

2. Set environment variables (optional):
```bash
export RME_CONFIG_PATH=/path/to/config.yaml
export RME_MODEL_PATH=/path/to/models
```

## Usage

### Starting the Server
```bash
python main.py
```
The server will start at `http://localhost:8000`

### API Endpoints

#### 1. Match Profiles
```http
POST /match
Content-Type: multipart/form-data

Parameters:
- job_description: string
- files: file[] (multiple files)
- use_ai: boolean (default: true)
- threshold: float (default: 0.7)

Response:
{
    "matches": [
        {
            "profile": "content...",
            "score": 0.85,
            "analysis": {...}
        }
    ],
    "analysis": {
        "total_candidates": 10,
        "matching_candidates": 5,
        "average_score": 0.75,
        "ai_enhanced": true
    },
    "metadata": {...}
}
```

#### 2. Analyze Profile
```http
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: file
- use_ai: boolean (default: true)

Response:
{
    "content": "extracted text...",
    "sections": {
        "summary": "...",
        "skills": "...",
        "experience": "...",
        "education": "...",
        "certifications": "..."
    },
    "metadata": {...},
    "ai_analysis": {...}
}
```

#### 3. Health Check
```http
GET /health

Response:
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2024-03-14T12:00:00Z"
}
```

### Python Client Example
```python
import requests

# Match profiles
files = [
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.docx', 'rb'))
]
data = {
    'job_description': 'Python developer with ML experience...',
    'use_ai': True,
    'threshold': 0.7
}
response = requests.post('http://localhost:8000/match', files=files, data=data)
matches = response.json()

# Analyze single profile
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/analyze',
        files={'file': f},
        data={'use_ai': True}
    )
analysis = response.json()
```

## Testing

Run the test suite:
   ```bash
pytest tests/
   ```

Run specific test categories:
```bash
pytest tests/test_enhanced_document_processor.py
pytest tests/test_ai_matching.py
pytest tests/test_integration.py
```

## Project Structure
```
rme/
├── src/
│   ├── enhanced_document_processor.py
│   ├── ai_enhanced_matching.py
│   ├── ai_matching_integration.py
│   ├── matching_engine.py
│   └── utils/
├── tests/
│   ├── test_enhanced_document_processor.py
│   ├── test_ai_matching.py
│   └── test_integration.py
├── models/
│   ├── skill_models/
│   └── ai_models/
├── docs/
│   ├── api.md
│   └── matching_results.md
├── scripts/
│   ├── download_models.py
│   └── setup.py
├── main.py
├── requirements.txt
├── config.yaml
└── README.md
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Open-source AI models and libraries
- FastAPI framework
- Python community
- Contributors and users 

# Resume Matching Engine Frontend

A modern, responsive web application for matching resumes to job descriptions using AI.

## Features

- **Modern UI/UX**: Built with Bootstrap 5 and Material Design Icons
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Offline Support**: Service worker implementation for offline functionality
- **Form Validation**: Client-side validation with Bootstrap's form validation
- **Error Handling**: Custom error pages for 404 and 500 errors
- **Accessibility**: ARIA labels and semantic HTML for better accessibility

## Directory Structure

```
frontend/
├── static/
│   ├── css/
│   │   └── main.css          # Main stylesheet
│   ├── js/
│   │   └── main.js           # Main JavaScript file
│   ├── images/
│   │   ├── icons/            # SVG icons
│   │   ├── testimonials/     # Testimonial user avatars
│   │   ├── logo.svg          # Application logo
│   │   ├── favicon.svg       # Favicon
│   │   ├── grid-pattern.svg  # Background pattern
│   │   ├── 404-illustration.svg
│   │   └── 500-illustration.svg
│   └── sw.js                 # Service worker
└── templates/
    ├── base.html             # Base template with common elements
    ├── index.html            # Landing page
    ├── upload.html           # Document upload page
    ├── matches.html          # Matches listing page
    ├── profile.html          # User profile page
    ├── offline.html          # Offline page
    ├── 404.html              # Not found error page
    └── 500.html              # Server error page
```

## Pages

### Base Template (`base.html`)
- Common layout structure
- Navigation bar
- Footer
- Service worker registration
- Common CSS and JavaScript includes

### Landing Page (`index.html`)
- Welcome message
- Feature cards
- Call-to-action buttons
- Quick start guide

### Upload Page (`upload.html`)
- Document upload form
- Job details form
- Client-side validation
- File type restrictions
- Loading states

### Matches Page (`matches.html`)
- Match listing table
- Filtering and sorting
- Match score visualization
- Bulk actions
- Pagination

### Profile Page (`profile.html`)
- User information
- Profile settings
- Security settings
- Connected accounts
- Activity history

### Error Pages
- 404 Not Found (`404.html`)
- 500 Server Error (`500.html`)
- Offline Page (`offline.html`)

## Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Bootstrap 5
- **JavaScript**: ES6+ with async/await
- **Bootstrap 5**: Responsive framework
- **Material Design Icons**: Icon set
- **Service Workers**: Offline support
- **Fetch API**: Modern HTTP requests

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

1. Clone the repository
2. Install dependencies (if any)
3. Start the development server
4. Access the application at `http://localhost:8001`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 