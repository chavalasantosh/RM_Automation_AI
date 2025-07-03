# RME Dashboard

An interactive dashboard for visualizing and analyzing resume matching results. This dashboard provides a comprehensive view of match results, skill analysis, experience analysis, and detailed match information.

## Features

### Overview Page
- Summary statistics (total matches, perfect matches, average score)
- Match score distribution visualization
- Match overview table with color-coded scores

### Skill Analysis Page
- Interactive skill match heatmap
- Detailed skill matrix showing required, matching, and missing skills
- Missing skills analysis with frequency visualization

### Experience Analysis Page
- Experience vs Match Score scatter plot
- Education distribution pie chart
- Experience timeline visualization

### Detailed Results Page
- Filterable results table with minimum score filter
- Export to Excel functionality (coming soon)
- Detailed analysis for selected matches
- Comprehensive skill matching breakdown

## Prerequisites

- Python 3.7 or higher
- Required packages (install using `pip install -r requirements.txt`):
  - streamlit
  - pandas
  - plotly
  - openpyxl (for Excel export)

## Installation

1. Ensure you have all required packages installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you have match results in the `output` directory (JSON files)

## Usage

1. Run the dashboard using the provided script:
   ```bash
   python run_dashboard.py
   ```

2. The dashboard will automatically open in your default web browser at `http://localhost:8501`

3. Navigate through different views using the sidebar menu

## Data Format

The dashboard expects match results in JSON format in the `output` directory. Each JSON file should contain:
- Job information
- Candidate profile
- Match scores
- Matching criteria details
- Required and matching skills

## Development

### Adding New Features

1. The dashboard is built using Streamlit and Plotly
2. Main application code is in `app.py`
3. To add new visualizations:
   - Add new functions to create required DataFrames
   - Add new pages to the navigation menu
   - Create visualizations using Plotly

### Running Tests

```bash
pytest tests/
```

## Troubleshooting

1. If the dashboard doesn't start:
   - Check if all required packages are installed
   - Verify that match results exist in the output directory
   - Check the console for error messages

2. If visualizations don't load:
   - Verify the data format in JSON files
   - Check browser console for JavaScript errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 