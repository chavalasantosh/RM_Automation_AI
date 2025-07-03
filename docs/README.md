# Project Documentation

## Overview
This project is a FastAPI-based application designed to manage and match skills, process documents, and handle project allocations. It includes features for uploading candidate resumes, creating project requirements, and managing allocations.

## Project Structure
- **app/**: Contains the main FastAPI application and related modules.
  - **main.py**: The entry point for the FastAPI application.
  - **services/**: Contains service modules for document processing, matching, decision-making, and notifications.
  - **models/**: Contains data models for candidates, projects, and allocations.
  - **core/**: Contains core configuration settings.
- **src/**: Contains utility modules for skill management, document processing, and visualizations.
- **tests/**: Contains unit and integration tests for the project.
- **docs/**: Contains project documentation.
- **data/**: Contains directories for uploads and visualizations.
- **alembic/**: Contains database migration files.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration
- The project uses a `config.yaml` file for configuration settings. Ensure this file is properly configured before running the application.

## Running the Application
1. Start the FastAPI server:
   ```sh
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Access the API documentation in your browser at:
   ```
   http://localhost:8000/docs
   ```

## Usage
- **Upload Candidate Resume**: Use the `/candidates/upload` endpoint to upload and process a candidate's resume.
- **Create Project Requirement**: Use the `/projects` endpoint to create a new project requirement.
- **Get Allocation Status**: Use the `/allocations/{allocation_id}` endpoint to check the status of a project allocation.
- **Get Project Allocations**: Use the `/projects/{project_id}/allocations` endpoint to get all allocations for a project.
- **Get Candidate Allocations**: Use the `/candidates/{candidate_id}/allocations` endpoint to get all allocations for a candidate.
- **Update Allocation Feedback**: Use the `/allocations/{allocation_id}/feedback` endpoint to update feedback for a completed allocation.

## Testing
- Run unit tests:
  ```sh
  pytest tests/unit
  ```
- Run integration tests:
  ```sh
  pytest tests/integration
  ```

## Contributing
- Fork the repository.
- Create a new branch for your feature.
- Commit your changes.
- Push to the branch.
- Create a Pull Request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or issues, please contact [your-email@example.com](mailto:your-email@example.com). 