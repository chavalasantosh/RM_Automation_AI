#!/usr/bin/env python3
"""
Email Template Documentation Generator

This script analyzes email template HTML files and generates a comprehensive HTML documentation page.
It performs static analysis of the template files to extract metadata, categorize templates,
and create an interactive documentation interface.

Usage: python generate_documentation.py
"""

import json
import os
import glob
import datetime
import re
from typing import Dict, List, Any, Optional, Tuple, Set

# Constants
DEFAULT_TEMPLATES_DIR = "templates/email"


class TemplateAnalyzer:
    """Analyzes email template HTML files and generates documentation data."""
    
    def __init__(self, templates_dir: str = DEFAULT_TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.templates = []
        self.stats = {
            'total': 0,
            'categories': {},
            'variables': set(),
            'total_sections': 0,
            'responsive_templates': 0,
            'has_cta': 0
        }
    
    def analyze_all_templates(self) -> Dict[str, Any]:
        """Analyze all template files and return comprehensive data."""
        if not os.path.exists(self.templates_dir):
            print(f"Warning: Templates directory '{self.templates_dir}' not found.")
            return self._get_empty_data()
        
        html_files = glob.glob(os.path.join(self.templates_dir, "*.html"))
        
        if not html_files:
            print(f"Warning: No HTML files found in '{self.templates_dir}' directory.")
            return self._get_empty_data()
        
        print(f"Found {len(html_files)} template files. Analyzing...")
        
        for file_path in html_files:
            try:
                template_data = self._analyze_template_file(file_path)
                if template_data:
                    self.templates.append(template_data)
            except Exception as e:
                print(f"Error analyzing {file_path}: {str(e)}")
                continue
        
        self._calculate_stats()
        
        return {
            'templates': self.templates,
            'stats': self.stats,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def _analyze_template_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single template file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            print(f"Error reading {file_path}: {str(e)}")
            return None
        
        filename = os.path.basename(file_path)
        template_name = filename.replace('.html', '')
        
        # Extract basic metadata
        template = {
            'filename': filename,
            'name': template_name.replace('_', ' ').title(),
            'category': self._determine_category(template_name),
            'sections': self._extract_sections(content),
            'variables': list(self._extract_variables(content)),
            'is_responsive': self._check_responsive(content),
            'has_cta': self._check_cta(content),
            'color_scheme': self._extract_color_scheme(content),
            'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        # Generate description
        template['description'] = self._generate_description(template)
        
        # Store raw content for viewer
        template['rawContent'] = content
        
        return template
    
    def _determine_category(self, template_name: str) -> str:
        """Determine the category of the template based on its name."""
        categories = {
            'welcome': 'Onboarding',
            'account_deleted': 'Account Management',
            'security_alert': 'Security',
            'password_changed': 'Security',
            'job_match': 'Job Alerts',
            'maintenance': 'System',
            'activity_summary': 'Account Management',
            'upload_notification': 'Document Management',
            'profile_reminder': 'Account Management',
            'announcement': 'System',
            'job_status_update': 'Job Alerts',
            'interview_invitation': 'Job Alerts',
            'feedback_request': 'Feedback',
            'thank_you': 'Communication',
            'job_application_received': 'Job Alerts',
            'account_activity_alert': 'Security'
        }
        
        return categories.get(template_name, 'Other')
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract main sections from the template."""
        sections = []
        # Look for common section patterns
        section_patterns = [
            r'class="header"',
            r'class="content"',
            r'class="footer"',
            r'class="[^"]*box"',
            r'class="[^"]*section"'
        ]
        
        for pattern in section_patterns:
            if re.search(pattern, content):
                section_name = pattern.split('"')[1].replace('class=', '').strip()
                if section_name not in sections:
                    sections.append(section_name)
        
        return sections
    
    def _extract_variables(self, content: str) -> Set[str]:
        """Extract template variables from the content."""
        variables = set()
        # Look for Django/Jinja2 style variables
        var_pattern = r'{{[^}]+}}'
        matches = re.finditer(var_pattern, content)
        
        for match in matches:
            var = match.group().strip('{}').strip()
            if var and not var.startswith('#'):  # Exclude comments
                variables.add(var)
        
        return variables
    
    def _check_responsive(self, content: str) -> bool:
        """Check if the template is responsive."""
        responsive_indicators = [
            'viewport',
            'media queries',
            '@media',
            'responsive',
            'max-width',
            'min-width'
        ]
        
        return any(indicator in content.lower() for indicator in responsive_indicators)
    
    def _check_cta(self, content: str) -> bool:
        """Check if the template has call-to-action buttons."""
        cta_indicators = [
            'class="btn"',
            'class="button"',
            'call-to-action',
            'cta'
        ]
        
        return any(indicator in content.lower() for indicator in cta_indicators)
    
    def _extract_color_scheme(self, content: str) -> Dict[str, Optional[str]]:
        """Extract the color scheme used in the template."""
        colors: Dict[str, Optional[str]] = {
            'primary': None,
            'secondary': None,
            'accent': None,
            'background': None,
            'text': None
        }
        
        # Look for color definitions in CSS
        color_patterns = {
            'primary': r'--primary-color:\s*([^;]+)',
            'secondary': r'--secondary-color:\s*([^;]+)',
            'accent': r'--accent-color:\s*([^;]+)',
            'background': r'background(?:-color)?:\s*([^;]+)',
            'text': r'color:\s*([^;]+)'
        }
        
        for color_type, pattern in color_patterns.items():
            match = re.search(pattern, content)
            if match:
                colors[color_type] = match.group(1).strip()
        
        return colors
    
    def _generate_description(self, template: Dict[str, Any]) -> str:
        """Generate a descriptive summary of the template."""
        name = template['name']
        category = template['category']
        sections = len(template['sections'])
        variables = len(template['variables'])
        
        desc = f"{name} template ({category}) with {sections} main sections"
        
        if template['is_responsive']:
            desc += ", responsive design"
        
        if template['has_cta']:
            desc += ", includes call-to-action"
        
        if variables > 0:
            desc += f", uses {variables} dynamic variables"
        
        return desc
    
    def _calculate_stats(self):
        """Calculate statistics from analyzed templates."""
        self.stats['total'] = len(self.templates)
        
        for template in self.templates:
            # Category count
            category = template['category']
            self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
            
            # Variables
            self.stats['variables'].update(template['variables'])
            
            # Section count
            self.stats['total_sections'] += len(template['sections'])
            
            # Responsive templates
            if template['is_responsive']:
                self.stats['responsive_templates'] += 1
            
            # Templates with CTA
            if template['has_cta']:
                self.stats['has_cta'] += 1
        
        # Convert variables set to list for JSON serialization
        self.stats['unique_variables'] = len(self.stats['variables'])
        self.stats['variables'] = sorted(list(self.stats['variables']))
    
    def _get_empty_data(self) -> Dict[str, Any]:
        """Return empty data structure when no templates found."""
        return {
            'templates': [],
            'stats': {
                'total': 0,
                'categories': {},
                'variables': [],
                'unique_variables': 0,
                'total_sections': 0,
                'responsive_templates': 0,
                'has_cta': 0
            },
            'timestamp': datetime.datetime.now().isoformat()
        }


def generate_html_documentation(data: Dict[str, Any]) -> str:
    """Generate the complete HTML documentation with embedded data."""
    
    # Convert Python data to JavaScript with proper escaping
    js_data = json.dumps(data, indent=2, ensure_ascii=False)
    js_data = js_data.replace('</script>', '<\\/script>').replace('<!--', '<\\!--')
    
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-color: #4a5568;
            --secondary-color: #6b7280;
            --accent-color: #5b77a3;
            --light-bg: #f8fafc;
            --dark-bg: #1e293b;
            --card-bg: #ffffff;
            --card-bg-dark: #334155;
            --text-primary: #1a202c;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --text-light: #ffffff;
            --border-color: #e2e8f0;
            --border-color-dark: #475569;
            --success-color: #059669;
            --warning-color: #d97706;
            --error-color: #dc2626;
            --info-color: #0ea5e9;
            --surface-hover: #f1f5f9;
            --surface-hover-dark: #475569;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--light-bg);
            color: var(--text-primary);
            min-height: 100vh;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .dark-mode {
            background: var(--dark-bg);
            color: var(--text-light);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 40px 30px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        .dark-mode .header {
            background: var(--card-bg-dark);
            border-color: var(--border-color-dark);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: var(--primary-color);
            font-weight: 700;
        }

        .header .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 20px;
        }

        .dark-mode .header .subtitle {
            color: var(--text-muted);
        }

        .header .timestamp {
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            align-items: center;
        }

        .search-container {
            flex: 1;
            min-width: 300px;
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 12px 45px 12px 20px;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            background: var(--card-bg);
            color: var(--text-primary);
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .dark-mode .search-input {
            border-color: var(--border-color-dark);
            background: var(--card-bg-dark);
            color: var(--text-light);
        }

        .search-input:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(91, 119, 163, 0.1);
        }

        .search-input::placeholder {
            color: var(--text-muted);
        }

        .search-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }

        .filter-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            font-weight: 500;
        }

        .dark-mode .filter-btn {
            border-color: var(--border-color-dark);
            background: var(--card-bg-dark);
            color: var(--text-light);
        }

        .filter-btn:hover {
            background: var(--surface-hover);
            border-color: var(--accent-color);
        }

        .dark-mode .filter-btn:hover {
            background: var(--surface-hover-dark);
        }

        .filter-btn.active {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: white;
            box-shadow: 0 2px 4px rgba(91, 119, 163, 0.2);
        }

        .theme-toggle {
            padding: 10px 20px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .dark-mode .theme-toggle {
            border-color: var(--border-color-dark);
            background: var(--card-bg-dark);
            color: var(--text-light);
        }

        .theme-toggle:hover {
            background: var(--surface-hover);
            border-color: var(--accent-color);
        }

        .dark-mode .theme-toggle:hover {
            background: var(--surface-hover-dark);
        }

        .stats-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px 20px;
            text-align: center;
            border: 1px solid var(--border-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .dark-mode .stat-card {
            background: var(--card-bg-dark);
            border-color: var(--border-color-dark);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .dark-mode .stat-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent-color);
            margin-bottom: 5px;
        }

        .stat-label {
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 500;
        }

        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
            overflow: visible;
        }

        .workflow-card {
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow: visible;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .dark-mode .workflow-card {
            background: var(--card-bg-dark);
            border-color: var(--border-color-dark);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .workflow-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            border-color: var(--accent-color);
        }

        .dark-mode .workflow-card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }

        .workflow-header {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .dark-mode .workflow-header {
            border-bottom-color: var(--border-color-dark);
        }

        .workflow-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text-primary);
        }

        .dark-mode .workflow-title {
            color: var(--text-light);
        }

        .workflow-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 10px;
        }

        .workflow-info {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-right: 8px;
            cursor: help;
            position: relative;
        }

        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            position: relative;
            flex-shrink: 0;
            display: inline-block;
        }

        .status-active {
            background-color: var(--success-color);
            box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
            animation: pulse-green 2s infinite;
        }

        .status-inactive {
            background-color: var(--text-muted);
            box-shadow: 0 0 0 2px rgba(113, 128, 150, 0.2);
        }

        .status-text {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 500;
        }

        .complexity-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }

        .complexity-low {
            background-color: var(--success-color);
        }

        .complexity-medium {
            background-color: var(--warning-color);
        }

        .complexity-high {
            background-color: var(--error-color);
        }

        .workflow-stats {
            display: flex;
            gap: 15px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .workflow-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 15px;
        }

        .dark-mode .workflow-description {
            color: var(--text-muted);
        }

        .workflow-footer {
            padding: 15px 20px;
            background: var(--surface-hover);
            border-radius: 0 0 12px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        .dark-mode .workflow-footer {
            background: var(--surface-hover-dark);
        }

        .workflow-tags {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .tag {
            background: var(--accent-color);
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .trigger-badge {
            background: var(--info-color);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .action-buttons {
            display: flex;
            gap: 8px;
        }

        .btn {
            padding: 6px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: var(--card-bg);
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .dark-mode .btn {
            border-color: var(--border-color-dark);
            background: var(--card-bg-dark);
            color: var(--text-light);
        }

        .btn:hover {
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }

        .expanded .workflow-details {
            display: block;
        }

        .workflow-details {
            display: none;
            padding: 20px;
            border-top: 1px solid var(--border-color);
            background: var(--light-bg);
        }

        .dark-mode .workflow-details {
            border-top-color: var(--border-color-dark);
            background: var(--dark-bg);
        }

        .details-section {
            margin-bottom: 20px;
        }

        .details-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--text-primary);
        }

        .dark-mode .details-title {
            color: var(--text-light);
        }

        .integrations-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .integration-tag {
            background: var(--secondary-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
        }

        @keyframes pulse-green {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
        }

        .modal-content {
            background-color: var(--card-bg);
            margin: 2% auto;
            padding: 0;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            width: 95%;
            max-width: 1200px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .dark-mode .modal-content {
            background-color: var(--card-bg-dark);
            border-color: var(--border-color-dark);
        }

        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface-hover);
            border-radius: 12px 12px 0 0;
        }

        .dark-mode .modal-header {
            background: var(--surface-hover-dark);
            border-bottom-color: var(--border-color-dark);
        }

        .modal-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .dark-mode .modal-title {
            color: var(--text-light);
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-muted);
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }

        .close-btn:hover {
            background: rgba(0, 0, 0, 0.1);
            color: var(--text-primary);
        }

        .dark-mode .close-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-light);
        }

        .modal-body {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .json-viewer {
            flex: 1;
            overflow: auto;
            padding: 20px;
            margin: 0;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            background: var(--light-bg);
            border: none;
            resize: none;
            white-space: pre;
            color: var(--text-primary);
            min-height: 0;
        }

        .dark-mode .json-viewer {
            background: var(--dark-bg);
            color: var(--text-light);
        }

        .legend-section {
            margin-bottom: 30px;
            padding: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }

        .dark-mode .legend-section {
            background: var(--card-bg-dark);
            border-color: var(--border-color-dark);
        }

        .legend-title {
            margin-bottom: 15px;
            color: var(--text-primary);
            font-size: 1rem;
            font-weight: 600;
        }

        .dark-mode .legend-title {
            color: var(--text-light);
        }

        .legend-grid {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            align-items: center;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-text {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .dark-mode .legend-text {
            color: var(--text-muted);
        }

        /* Utility classes for common patterns */
        .border-radius-md {
            border-radius: 12px;
        }

        .border-radius-sm {
            border-radius: 8px;
        }

        .padding-20 {
            padding: 20px;
        }

        .margin-bottom-20 {
            margin-bottom: 20px;
        }

        .margin-bottom-30 {
            margin-bottom: 30px;
        }

        .card-bg {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
        }

        .dark-mode .card-bg {
            background: var(--card-bg-dark);
            border-color: var(--border-color-dark);
        }

        .shadow-sm {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .dark-mode .shadow-sm {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .shadow-md {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        .dark-mode .shadow-md {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }

        .modal-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            background: var(--surface-hover);
            border-radius: 0 0 12px 12px;
        }

        .dark-mode .modal-footer {
            border-top-color: var(--border-color-dark);
            background: var(--surface-hover-dark);
        }

        .loading {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            font-size: 1.1rem;
        }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }

        .no-results h3 {
            margin-bottom: 10px;
            color: var(--text-secondary);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .header {
                padding: 30px 20px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .controls {
                flex-direction: column;
                align-items: stretch;
            }

            .workflow-grid {
                grid-template-columns: 1fr;
            }

            .workflow-meta {
                flex-direction: column;
                align-items: flex-start;
            }

            .modal-content {
                width: 98%;
                height: 95vh;
                margin: 1% auto;
            }

            .legend-grid {
                gap: 15px;
            }

            .legend-item {
                flex-basis: 100%;
            }
        }

        /* Additional styles for email template documentation */
        .template-preview {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            max-height: 300px;
            overflow: auto;
        }
        
        .variable-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .variable-tag {
            background: #e9ecef;
            color: #495057;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-family: monospace;
        }
        
        .color-scheme {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .color-box {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
        }
        
        .section-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .section-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 Email Template Documentation</h1>
            <p class="subtitle">Comprehensive analysis and documentation of email templates</p>
            <p class="timestamp" id="generatedTimestamp">Generated: Loading...</p>
        </div>

        <div class="controls">
            <div class="search-container">
                <input type="text" id="searchInput" class="search-input" placeholder="Search templates by name, category, or variable...">
                <span class="search-icon">🔍</span>
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="Onboarding">Onboarding</button>
                <button class="filter-btn" data-filter="Security">Security</button>
                <button class="filter-btn" data-filter="Job Alerts">Job Alerts</button>
                <button class="filter-btn" data-filter="System">System</button>
                <button class="filter-btn" data-filter="Account Management">Account Management</button>
            </div>
            <button class="theme-toggle" id="themeToggle">🌙 Dark</button>
        </div>

        <div class="stats-dashboard">
            <div class="stat-card">
                <div class="stat-number" id="totalTemplates">0</div>
                <div class="stat-label">Total Templates</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="responsiveTemplates">0</div>
                <div class="stat-label">Responsive Templates</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalVariables">0</div>
                <div class="stat-label">Unique Variables</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalSections">0</div>
                <div class="stat-label">Total Sections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="templatesWithCTA">0</div>
                <div class="stat-label">Templates with CTA</div>
            </div>
        </div>

        <div class="legend-section">
            <h3 class="legend-title">Template Categories</h3>
            <div class="legend-grid">
                <div class="legend-item">
                    <span class="section-tag">Onboarding</span>
                    <span class="legend-text">Welcome emails and initial setup</span>
                </div>
                <div class="legend-item">
                    <span class="section-tag">Security</span>
                    <span class="legend-text">Security alerts and account protection</span>
                </div>
                <div class="legend-item">
                    <span class="section-tag">Job Alerts</span>
                    <span class="legend-text">Job-related notifications and updates</span>
                </div>
                <div class="legend-item">
                    <span class="section-tag">System</span>
                    <span class="legend-text">System maintenance and announcements</span>
                </div>
                <div class="legend-item">
                    <span class="section-tag">Account Management</span>
                    <span class="legend-text">Account updates and management</span>
                </div>
            </div>
        </div>

        <div class="loading" id="loadingIndicator">
            <p>📧 Analyzing templates...</p>
        </div>

        <div class="workflow-grid" id="templateGrid" style="display: none;">
            <!-- Template cards will be generated here -->
        </div>

        <div class="no-results" id="noResults" style="display: none;">
            <h3>No templates found</h3>
            <p>Try adjusting your search terms or filters</p>
        </div>
    </div>

    <!-- Template Viewer Modal -->
    <div id="templateModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle">Template Preview</h2>
                <button class="close-btn" id="closeModal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="template-preview" id="templatePreview"></div>
            </div>
            <div class="modal-footer">
                <button class="btn" id="copyTemplate">📋 Copy</button>
                <button class="btn" id="downloadTemplate">💾 Download</button>
            </div>
        </div>
    </div>

    <script>
        // Embedded workflow data from Python analysis
        const TEMPLATE_DATA = ''' + js_data + ''';

        class TemplateDocumentation {
            constructor() {
                this.templates = TEMPLATE_DATA.templates || [];
                this.stats = TEMPLATE_DATA.stats || {};
                this.filteredTemplates = this.templates;
                this.currentFilter = 'all';
                this.currentSearch = '';
                
                this.init();
            }

            init() {
                this.renderStats();
                this.renderTemplates();
                this.setupEventListeners();
                this.hideLoading();
                this.updateTimestamp();
            }

            updateTimestamp() {
                const timestamp = TEMPLATE_DATA.timestamp || new Date().toISOString();
                const date = new Date(timestamp);
                document.getElementById('generatedTimestamp').textContent = 
                    `Generated: ${date.toLocaleDateString()} at ${date.toLocaleTimeString()}`;
            }

            renderStats() {
                document.getElementById('totalTemplates').textContent = this.stats.total || 0;
                document.getElementById('responsiveTemplates').textContent = this.stats.responsive_templates || 0;
                document.getElementById('totalVariables').textContent = this.stats.unique_variables || 0;
                document.getElementById('totalSections').textContent = this.stats.total_sections || 0;
                document.getElementById('templatesWithCTA').textContent = this.stats.has_cta || 0;
            }

            renderTemplates() {
                const grid = document.getElementById('templateGrid');
                const noResults = document.getElementById('noResults');
                
                if (this.filteredTemplates.length === 0) {
                    grid.style.display = 'none';
                    noResults.style.display = 'block';
                    return;
                }

                grid.style.display = 'grid';
                noResults.style.display = 'none';
                
                grid.innerHTML = this.filteredTemplates.map(template => this.createTemplateCard(template)).join('');
            }

            createTemplateCard(template) {
                const statusClass = template.active ? 'status-active' : 'status-inactive';
                const statusText = template.active ? 'Active' : 'Inactive';
                const statusTooltip = template.active ? 'Active - Template will be used when triggered' : 'Inactive - Template is disabled';
                const complexityClass = `complexity-${template.complexity}`;
                
                const tags = template.tags.map(tag => 
                    `<span class="tag">${typeof tag === 'string' ? tag : tag.name}</span>`
                ).join('');

                const integrations = template.integrations.slice(0, 5).map(integration => 
                    `<span class="integration-tag">${integration}</span>`
                ).join('');

                return `
                    <div class="workflow-card" data-trigger="${template.triggerType}" data-name="${template.name.toLowerCase()}" data-description="${template.description.toLowerCase()}" data-integrations="${template.integrations.join(' ').toLowerCase()}">
                        <div class="workflow-header">
                            <div class="workflow-meta">
                                <div class="workflow-info">
                                    <div class="status-indicator" title="${statusTooltip}">
                                        <div class="status-dot ${statusClass}"></div>
                                        <span class="status-text">${statusText}</span>
                                    </div>
                                    <div class="workflow-stats">
                                        <span><div class="complexity-indicator ${complexityClass}"></div>${template.nodeCount} nodes</span>
                                        <span>📁 ${template.filename}</span>
                                    </div>
                                </div>
                                <span class="trigger-badge">${template.triggerType}</span>
                            </div>
                            <h3 class="workflow-title">${template.name}</h3>
                            <p class="workflow-description">${template.description}</p>
                        </div>
                        
                        <div class="workflow-details">
                            <div class="details-section">
                                <h4 class="details-title">Integrations (${template.integrations.length})</h4>
                                <div class="integrations-list">
                                    ${integrations}
                                    ${template.integrations.length > 5 ? `<span class="integration-tag">+${template.integrations.length - 5} more</span>` : ''}
                                </div>
                            </div>
                            ${template.tags.length > 0 ? `
                                <div class="details-section">
                                    <h4 class="details-title">Tags</h4>
                                    <div class="workflow-tags">${tags}</div>
                                </div>
                            ` : ''}
                            ${template.createdAt ? `
                                <div class="details-section">
                                    <h4 class="details-title">Metadata</h4>
                                    <div style="font-size: 0.85rem; color: var(--text-muted);">
                                        <p>Created: ${new Date(template.createdAt).toLocaleDateString()}</p>
                                        ${template.updatedAt ? `<p>Updated: ${new Date(template.updatedAt).toLocaleDateString()}</p>` : ''}
                                        ${template.versionId ? `<p>Version: ${template.versionId.substring(0, 8)}...</p>` : ''}
                                    </div>
                                </div>
                            ` : ''}
                        </div>

                        <div class="workflow-footer">
                            <div class="workflow-tags">${tags}</div>
                            <div class="action-buttons">
                                <button class="btn toggle-details">View Details</button>
                                <button class="btn view-json" data-workflow-name="${template.name}" data-filename="${template.filename}">View File</button>
                            </div>
                        </div>
                    </div>
                `;
            }

            setupEventListeners() {
                // Search functionality
                document.getElementById('searchInput').addEventListener('input', (e) => {
                    this.currentSearch = e.target.value.toLowerCase();
                    this.filterTemplates();
                });

                // Filter buttons
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        this.currentFilter = e.target.dataset.filter;
                        this.filterTemplates();
                    });
                });

                // Theme toggle
                document.getElementById('themeToggle').addEventListener('click', this.toggleTheme);

                // Workflow card interactions
                document.addEventListener('click', (e) => {
                    if (e.target.classList.contains('toggle-details')) {
                        const card = e.target.closest('.workflow-card');
                        card.classList.toggle('expanded');
                        e.target.textContent = card.classList.contains('expanded') ? 'Hide Details' : 'View Details';
                    }

                    if (e.target.classList.contains('view-json')) {
                        const workflowName = e.target.dataset.workflowName;
                        const filename = e.target.dataset.filename;
                        this.showJsonModal(workflowName, filename);
                    }
                });

                // Modal functionality
                document.getElementById('closeModal').addEventListener('click', this.hideJsonModal);
                document.getElementById('templateModal').addEventListener('click', (e) => {
                    if (e.target === e.currentTarget) this.hideJsonModal();
                });
                document.getElementById('copyTemplate').addEventListener('click', this.copyTemplateToClipboard);
                document.getElementById('downloadTemplate').addEventListener('click', this.downloadTemplate);

                // Escape key to close modal
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') this.hideJsonModal();
                });
            }

            filterTemplates() {
                this.filteredTemplates = this.templates.filter(template => {
                    const matchesFilter = this.currentFilter === 'all' || template.category === this.currentFilter;
                    const matchesSearch = !this.currentSearch || 
                        template.name.toLowerCase().includes(this.currentSearch) ||
                        template.description.toLowerCase().includes(this.currentSearch) ||
                        template.integrations.some(integration => 
                            integration.toLowerCase().includes(this.currentSearch)
                        ) ||
                        template.filename.toLowerCase().includes(this.currentSearch);
                    
                    return matchesFilter && matchesSearch;
                });

                this.renderTemplates();
            }

            showJsonModal(workflowName, filename) {
                const template = this.templates.find(t => t.name === workflowName);
                if (!template) return;

                document.getElementById('modalTitle').textContent = `${workflowName} - Template Preview`;
                document.getElementById('templatePreview').innerHTML = template.rawContent;
                document.getElementById('templateModal').style.display = 'block';
                document.body.style.overflow = 'hidden';
            }

            hideJsonModal() {
                document.getElementById('templateModal').style.display = 'none';
                document.body.style.overflow = 'auto';
            }

            copyTemplateToClipboard() {
                const templatePreview = document.getElementById('templatePreview');
                const templateContent = templatePreview.innerHTML;
                
                const textarea = document.createElement('textarea');
                textarea.value = templateContent;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                
                const btn = document.getElementById('copyTemplate');
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            }

            downloadTemplate() {
                const templateContent = document.getElementById('templatePreview').innerHTML;
                const templateName = document.getElementById('modalTitle').textContent.split(' - ')[0];
                const filename = `${templateName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.html`;
                
                const blob = new Blob([templateContent], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }

            toggleTheme() {
                document.body.classList.toggle('dark-mode');
                const isDark = document.body.classList.contains('dark-mode');
                document.getElementById('themeToggle').textContent = isDark ? '☀️ Light' : '🌙 Dark';
                localStorage.setItem('darkMode', isDark);
            }

            hideLoading() {
                document.getElementById('loadingIndicator').style.display = 'none';
                document.getElementById('templateGrid').style.display = 'grid';
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', () => {
            // Load saved theme preference
            if (localStorage.getItem('darkMode') === 'true') {
                document.body.classList.add('dark-mode');
                document.getElementById('themeToggle').textContent = '☀️ Light';
            }

            // Initialize the documentation
            new TemplateDocumentation();
        });
    </script>
</body>
</html>'''
    
    return html_template


def main():
    """Main function to generate the template documentation."""
    print("🔍 Email Template Documentation Generator")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = TemplateAnalyzer()
    
    # Analyze templates
    data = analyzer.analyze_all_templates()
    
    # Generate HTML
    print("📝 Generating HTML documentation...")
    html_content = generate_html_documentation(data)
    
    # Write HTML file
    output_file = "email-template-documentation.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Documentation generated successfully!")
    print(f"📄 Output file: {output_file}")
    print(f"📊 Analyzed {data['stats']['total']} templates")
    print(f"🔗 Open {output_file} in your browser to view the documentation")


if __name__ == "__main__":
    main()