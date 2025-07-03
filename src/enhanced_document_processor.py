from .document_processor import DocumentProcessor
import re

class EnhancedDocumentProcessor(DocumentProcessor):
    """Enhanced document processor with additional capabilities."""
    
    def __init__(self):
        """Initialize the enhanced document processor."""
        super().__init__()
        
    def extract_skills(self, text):
        """Extract skills from text using a simple keyword match."""
        skill_keywords = [
            'python', 'java', 'sql', 'excel', 'communication', 'leadership',
            'project management', 'machine learning', 'data analysis', 'c++', 'cloud', 'aws', 'azure', 'linux'
        ]
        found = set()
        for kw in skill_keywords:
            if re.search(rf'\\b{re.escape(kw)}\\b', text, re.IGNORECASE):
                found.add(kw)
        return list(found)
        
    def extract_experience(self, text):
        """Extract years of experience from text using regex."""
        matches = re.findall(r'(\\d+)\\s*\+?\\s*years?', text, re.IGNORECASE)
        years = [int(m) for m in matches]
        return max(years) if years else 0
        
    def extract_education(self, text):
        """Extract education level from text using keyword search."""
        education_levels = [
            'phd', 'doctorate', 'masters', 'bachelor', 'associate', 'diploma', 'high school'
        ]
        for level in education_levels:
            if re.search(rf'\\b{re.escape(level)}\\b', text, re.IGNORECASE):
                return level.title()
        return 'Not specified' 