from typing import Tuple, Dict, Any
from fastapi import UploadFile
import PyPDF2
import docx
import spacy
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import json

logger = logging.getLogger(__name__)

# Load models
try:
    nlp = spacy.load("en_core_web_sm")
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

async def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from PDF file."""
    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

async def extract_text_from_docx(file: UploadFile) -> str:
    """Extract text from DOCX file."""
    try:
        content = await file.read()
        doc = docx.Document(content)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise

async def extract_text_from_txt(file: UploadFile) -> str:
    """Extract text from TXT file."""
    try:
        content = await file.read()
        return content.decode("utf-8")
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {str(e)}")
        raise

async def process_document(file: UploadFile) -> Tuple[str, Dict[str, Any]]:
    """Process uploaded document and extract text and metadata."""
    try:
        # Extract text based on file type
        if file.filename.lower().endswith(".pdf"):
            text = await extract_text_from_pdf(file)
        elif file.filename.lower().endswith(".docx"):
            text = await extract_text_from_docx(file)
        elif file.filename.lower().endswith(".txt"):
            text = await extract_text_from_txt(file)
        else:
            raise ValueError("Unsupported file type")
        
        # Process text with spaCy
        doc = nlp(text)
        
        # Extract metadata
        metadata = {
            "entities": [
                {"text": ent.text, "label": ent.label_}
                for ent in doc.ents
            ],
            "skills": extract_skills(doc),
            "education": extract_education(doc),
            "experience": extract_experience(doc),
            "summary": generate_summary(doc)
        }
        
        return text, metadata
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def extract_skills(doc: spacy.tokens.Doc) -> list:
    """Extract skills from document."""
    # Load skills from skills.yaml
    with open("skills.yaml", "r") as f:
        skills_data = json.load(f)
    
    # Extract skills using spaCy
    skills = []
    for skill in skills_data["skills"]:
        if skill["name"].lower() in doc.text.lower():
            skills.append({
                "name": skill["name"],
                "category": skill["category"],
                "level": skill["level"]
            })
    return skills

def extract_education(doc: spacy.tokens.Doc) -> list:
    """Extract education information from document."""
    education = []
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"] and any(word in ent.text.lower() for word in ["university", "college", "school", "institute"]):
            education.append({
                "institution": ent.text,
                "degree": None,  # TODO: Implement degree extraction
                "year": None  # TODO: Implement year extraction
            })
    return education

def extract_experience(doc: spacy.tokens.Doc) -> list:
    """Extract work experience from document."""
    experience = []
    # TODO: Implement experience extraction using NLP
    return experience

def generate_summary(doc: spacy.tokens.Doc) -> str:
    """Generate a summary of the document."""
    # TODO: Implement summary generation using NLP
    return doc.text[:200] + "..."

def get_embedding(text: str) -> np.ndarray:
    """Get embedding for text using sentence transformer."""
    try:
        # Tokenize and get model output
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Mean pooling
        token_embeddings = outputs.last_hidden_state
        mask = inputs["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * mask, 1)
        sum_mask = torch.sum(mask, 1)
        mean_embeddings = sum_embeddings / sum_mask
        
        return mean_embeddings.numpy()
    except Exception as e:
        logger.error(f"Error getting embedding: {str(e)}")
        raise

async def match_documents(profile_text: str, job_text: str) -> Tuple[float, Dict[str, Any]]:
    """Match profile against job description."""
    try:
        # Get embeddings
        profile_embedding = get_embedding(profile_text)
        job_embedding = get_embedding(job_text)
        
        # Calculate similarity
        similarity = cosine_similarity(profile_embedding, job_embedding)[0][0]
        
        # Generate analysis
        analysis = {
            "similarity_score": float(similarity),
            "profile_summary": generate_summary(nlp(profile_text)),
            "job_summary": generate_summary(nlp(job_text)),
            "matching_skills": extract_matching_skills(profile_text, job_text),
            "missing_skills": extract_missing_skills(profile_text, job_text)
        }
        
        return similarity, analysis
    except Exception as e:
        logger.error(f"Error matching documents: {str(e)}")
        raise

def extract_matching_skills(profile_text: str, job_text: str) -> list:
    """Extract skills that match between profile and job."""
    profile_doc = nlp(profile_text)
    job_doc = nlp(job_text)
    
    profile_skills = set(skill["name"].lower() for skill in extract_skills(profile_doc))
    job_skills = set(skill["name"].lower() for skill in extract_skills(job_doc))
    
    return list(profile_skills.intersection(job_skills))

def extract_missing_skills(profile_text: str, job_text: str) -> list:
    """Extract skills required by job but missing in profile."""
    profile_doc = nlp(profile_text)
    job_doc = nlp(job_text)
    
    profile_skills = set(skill["name"].lower() for skill in extract_skills(profile_doc))
    job_skills = set(skill["name"].lower() for skill in extract_skills(job_doc))
    
    return list(job_skills - profile_skills) 