"""
Consolidated Matching Engine for RME
Combines functionality from all matching engine versions with improved error handling.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
from .skill_categories import SkillRegistry, Skill, SkillCategory, SkillLevel
from datetime import datetime, timezone
from pathlib import Path
import json
import yaml
import torch
from transformers import AutoTokenizer, AutoModel
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import warnings
from .enhanced_document_processor import EnhancedDocumentProcessor

logger = logging.getLogger(__name__)

class MatchingEngine:
    """Enhanced matching engine with AI capabilities."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_path: str = "models",
        device: Optional[str] = None,
        max_workers: int = 4,
        cache_size: int = 1000
    ):
        """Initialize the matching engine."""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.model_path = Path(model_path)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache_size = cache_size
        
        # Initialize document processor
        self.doc_processor = EnhancedDocumentProcessor()
        
        # Initialize models
        self._load_models()
        
        # Initialize caches
        self._init_caches()
        
        # Initialize weights
        self.weights = self._normalize_weights(self.config.get('weights'))
        
    def _load_models(self) -> None:
        """Load required models with error handling."""
        try:
            # Load sentence transformer model
            self.sentence_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device=self.device,
                cache_folder=str(self.model_path)
            )
            
            # Load BERT model for detailed analysis
            self.tokenizer = AutoTokenizer.from_pretrained(
                'bert-base-uncased',
                cache_dir=str(self.model_path)
            )
            self.bert_model = AutoModel.from_pretrained(
                'bert-base-uncased',
                cache_dir=str(self.model_path)
            ).to(self.device)
            
            logger.info("Successfully loaded all models")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
            
    def _init_caches(self) -> None:
        """Initialize caching for embeddings and results."""
        self.embedding_cache = {}
        self.result_cache = {}
        self.skill_cache = {}
        
    def _get_cached_embedding(self, text: str, cache: Dict[str, np.ndarray]) -> Optional[np.ndarray]:
        """Get cached embedding or compute new one."""
        if not text.strip():
            return None
            
        # Use text hash as key
        text_hash = hash(text.strip())
        
        # Check cache
        if text_hash in cache:
            return cache[text_hash]
            
        try:
            # Compute embedding
            embedding = self.sentence_model.encode(text, convert_to_numpy=True)
            
            # Update cache
            if len(cache) >= self.cache_size:
                # Remove oldest entry
                cache.pop(next(iter(cache)))
            cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error computing embedding: {str(e)}")
            return None
            
    def match(self, job_description: str, candidate_profile: str) -> Dict[str, Any]:
        """Match a candidate profile against a job description."""
        try:
            if not job_description.strip() or not candidate_profile.strip():
                raise ValueError("Job description and candidate profile must not be empty")
                
            # Process job description
            job_sections = self.doc_processor.extract_sections(job_description)
            if not job_sections:
                raise ValueError("Could not extract sections from job description")
                
            # Process candidate profile
            profile_sections = self.doc_processor.extract_sections(candidate_profile)
            if not profile_sections:
                raise ValueError("Could not extract sections from candidate profile")
                
            # Compute section scores
            section_scores = {}
            for section, weight in self.weights.items():
                if section in job_sections and section in profile_sections:
                    job_text = job_sections[section]
                    profile_text = profile_sections[section]
                    
                    if job_text.strip() and profile_text.strip():
                        # Get embeddings
                        job_embedding = self._get_cached_embedding(job_text, self.embedding_cache)
                        profile_embedding = self._get_cached_embedding(profile_text, self.embedding_cache)
                        
                        if job_embedding is not None and profile_embedding is not None:
                            # Compute similarity
                            similarity = cosine_similarity(
                                job_embedding.reshape(1, -1),
                                profile_embedding.reshape(1, -1)
                            )[0][0]
                            
                            section_scores[section] = float(similarity)
                            
            # Compute overall score
            if not section_scores:
                overall_score = 0.0
            else:
                overall_score = sum(
                    score * self.weights.get(section, 0.0)
                    for section, score in section_scores.items()
                )
                
            # Extract skills
            job_skills = self._extract_skills(job_sections.get('skills', ''))
            profile_skills = self._extract_skills(profile_sections.get('skills', ''))
            
            # Find matching and missing skills
            matching_skills = list(set(job_skills) & set(profile_skills))
            missing_skills = list(set(job_skills) - set(profile_skills))
            
            return {
                'score': float(overall_score),
                'section_scores': section_scores,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in match: {str(e)}")
            return {
                'error': str(e),
                'score': 0.0,
                'section_scores': {},
                'matching_skills': [],
                'missing_skills': [],
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
    def _extract_skills(self, text: str) -> List[str]:
        """Extract individual skills from text."""
        try:
            # Split by common delimiters
            skills = re.split(r'[,;|/]|\band\b', text.lower())
            
            # Clean and normalize
            skills = [
                skill.strip()
                for skill in skills
                if skill.strip()
            ]
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(skills))
            
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return []
            
    def _normalize_weights(self, weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        """Normalize matching weights."""
        default_weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'certifications': 0.1
        }
        
        if not weights:
            return default_weights
            
        # Ensure all required sections are present
        for section in default_weights:
            if section not in weights:
                weights[section] = default_weights[section]
                
        # Normalize to sum to 1.0
        total = sum(weights.values())
        if total == 0:
            return default_weights
            
        return {
            section: weight / total
            for section, weight in weights.items()
        }
        
    def __del__(self):
        """Cleanup resources."""
        try:
            self.executor.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Error shutting down executor: {str(e)}")
    
    def _validate_input(self, job_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate input data for matching."""
        required_fields = {
            'job_data': ['title', 'description', 'required_skills'],
            'profile_data': ['skills', 'years_of_experience', 'education']
        }
        
        # Check job data
        for field in required_fields['job_data']:
            if field not in job_data:
                return False, f"Missing required field '{field}' in job data"
        
        # Check profile data
        for field in required_fields['profile_data']:
            if field not in profile_data:
                return False, f"Missing required field '{field}' in profile data"
        
        return True, ""
    
    def _calculate_skill_match(self, job_skills: List[str], profile_skills: List[str]) -> float:
        """Calculate skill match score with improved matching."""
        if not job_skills or not profile_skills:
            return 0.0
            
        # Convert to sets for faster operations
        job_skill_set = set(s.lower() for s in job_skills)
        profile_skill_set = set(s.lower() for s in profile_skills)
        
        # Calculate exact matches
        exact_matches = len(job_skill_set.intersection(profile_skill_set))
        
        # Calculate partial matches using skill registry if available
        partial_matches = 0
        if self.skill_registry:
            for job_skill in job_skill_set:
                skill = self.skill_registry.get_skill(job_skill)
                if skill:
                    # Check aliases and tags
                    for profile_skill in profile_skill_set:
                        if (profile_skill in skill.aliases or 
                            any(tag in profile_skill for tag in skill.tags)):
                            partial_matches += 0.5  # Partial match weight
        
        # Calculate semantic similarity for remaining skills
        remaining_job_skills = list(job_skill_set - profile_skill_set)
        remaining_profile_skills = list(profile_skill_set - job_skill_set)
        
        if remaining_job_skills and remaining_profile_skills:
            try:
                # Get embeddings
                job_embeddings = self.sentence_model.encode(remaining_job_skills)
                profile_embeddings = self.sentence_model.encode(remaining_profile_skills)
                
                # Calculate similarity matrix
                similarity_matrix = cosine_similarity(job_embeddings, profile_embeddings)
                
                # Get maximum similarity for each job skill
                semantic_matches = np.max(similarity_matrix, axis=1)
                
                # Count matches above threshold
                semantic_match_count = np.sum(semantic_matches > 0.7)
                semantic_score = semantic_match_count * 0.3  # Semantic match weight
            except Exception as e:
                logger.warning(f"Error in semantic matching: {str(e)}")
                semantic_score = 0
        else:
            semantic_score = 0
        
        # Calculate final score
        total_skills = len(job_skill_set)
        if total_skills == 0:
            return 0.0
            
        score = (exact_matches + partial_matches + semantic_score) / total_skills
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_experience_match(self, required_years: float, actual_years: float) -> float:
        """Calculate experience match score with improved logic."""
        if required_years <= 0:
            return 1.0  # No experience requirement
            
        if actual_years >= required_years * 1.5:
            return 1.0  # More than enough experience
        elif actual_years >= required_years:
            return 0.8 + (actual_years - required_years) / (required_years * 0.5) * 0.2
        else:
            return max(0.0, actual_years / required_years)
    
    def _calculate_education_match(self, required_edu: str, actual_edu: str) -> float:
        """Calculate education match score with improved logic."""
        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        required_level = education_levels.get(required_edu.lower(), 0)
        actual_level = education_levels.get(actual_edu.lower(), 0)
        
        if actual_level >= required_level:
            return 1.0
        elif actual_level == required_level - 1:
            return 0.7
        elif actual_level == required_level - 2:
            return 0.4
        else:
            return 0.0
    
    def _calculate_certification_match(self, required_certs: List[str], actual_certs: List[str]) -> float:
        """Calculate certification match score."""
        if not required_certs:
            return 1.0  # No certification requirement
            
        if not actual_certs:
            return 0.0  # No certifications
            
        # Convert to sets for case-insensitive matching
        required_set = set(c.lower() for c in required_certs)
        actual_set = set(c.lower() for c in actual_certs)
        
        matches = len(required_set.intersection(actual_set))
        return matches / len(required_set)
    
    def batch_match(self, jobs: List[Dict[str, Any]], profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match multiple jobs with multiple profiles.
        
        Args:
            jobs: List of job dictionaries
            profiles: List of profile dictionaries
            
        Returns:
            List of match results
        """
        results = []
        total_matches = len(jobs) * len(profiles)
        processed = 0
        
        for job in jobs:
            for profile in profiles:
                try:
                    result = self.match(job['description'], profile['content'])
                    result['job'] = job['title']
                    result['profile'] = profile['name']
                    results.append(result)
                    
                    processed += 1
                    if processed % 10 == 0:
                        logger.info(f"Processed {processed}/{total_matches} matches")
                        
                except Exception as e:
                    logger.error(f"Error matching job {job['title']} with profile {profile['name']}: {str(e)}")
                    continue
        
        return results 