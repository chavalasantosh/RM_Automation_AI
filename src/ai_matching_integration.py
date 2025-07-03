from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
import json
import yaml
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import warnings
import re
from .matching_engine import MatchingEngine
from .enhanced_document_processor import EnhancedDocumentProcessor

logger = logging.getLogger(__name__)

def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class AIMatchingIntegration:
    """AI-enhanced matching integration with advanced analysis capabilities."""
    
    def __init__(
        self,
        model_path: str = "models",
        device: Optional[str] = None,
        max_workers: int = 4,
        cache_size: int = 1000
    ):
        """Initialize the AI matching integration."""
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache_size = cache_size
        
        # Initialize components
        self.matching_engine = MatchingEngine(
            model_path=str(self.model_path),
            device=self.device,
            max_workers=max_workers,
            cache_size=cache_size
        )
        
        self.doc_processor = EnhancedDocumentProcessor(
            model_path=str(self.model_path),
            device=self.device,
            max_workers=max_workers
        )
        
        # Initialize AI models
        self._load_models()
        
    def _load_models(self) -> None:
        """Load required AI models with error handling."""
        try:
            # Load BERT model for detailed analysis
            self.tokenizer = AutoTokenizer.from_pretrained(
                'bert-base-uncased',
                cache_dir=str(self.model_path)
            )
            self.bert_model = AutoModel.from_pretrained(
                'bert-base-uncased',
                cache_dir=str(self.model_path)
            ).to(self.device)
            
            # Load sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                'sentiment-analysis',
                model='distilbert-base-uncased-finetuned-sst-2-english',
                device=0 if self.device == 'cuda' else -1
            )
            
            # Load NER pipeline
            self.ner_analyzer = pipeline(
                'ner',
                model='dbmdz/bert-large-cased-finetuned-conll03-english',
                device=0 if self.device == 'cuda' else -1
            )
            
            logger.info("Successfully loaded all AI models")
            
        except Exception as e:
            logger.error(f"Error loading AI models: {str(e)}")
            raise
            
    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """Perform comprehensive AI analysis of content."""
        try:
            # Extract sections
            sections = self.doc_processor.extract_sections(content)
            
            # Analyze each section
            analysis_tasks = []
            for section, text in sections.items():
                if text.strip():
                    task = asyncio.create_task(
                        self._analyze_section(section, text)
                    )
                    analysis_tasks.append(task)
                    
            # Gather results
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            analysis = {}
            for i, (section, result) in enumerate(zip(sections.keys(), results)):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing {section}: {str(result)}")
                    analysis[section] = {'error': str(result)}
                else:
                    analysis[section] = result
                    
            # Add overall analysis
            analysis['overall'] = await self._analyze_overall(content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_content: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_section(self, section: str, text: str) -> Dict[str, Any]:
        """Analyze a specific section of content."""
        try:
            # Perform different analyses based on section type
            if section == 'skills':
                return await self._analyze_skills_section(text)
            elif section == 'experience':
                return await self._analyze_experience_section(text)
            elif section == 'education':
                return await self._analyze_education_section(text)
            else:
                return await self._analyze_general_section(text)
                
        except Exception as e:
            logger.error(f"Error analyzing {section} section: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_skills_section(self, text: str) -> Dict[str, Any]:
        """Analyze skills section with AI."""
        try:
            # Extract skills
            skills = self.matching_engine._extract_skills(text)
            
            # Analyze each skill
            skill_analysis = {}
            for skill in skills:
                # Get sentiment
                sentiment = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.sentiment_analyzer,
                    skill
                )[0]
                
                # Get NER tags
                entities = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.ner_analyzer,
                    skill
                )
                
                skill_analysis[skill] = {
                    'sentiment': sentiment,
                    'entities': entities
                }
                
            # Compute overall metrics
            sentiment_scores = [
                float(analysis['sentiment']['score'])
                for analysis in skill_analysis.values()
            ]
            
            return {
                'skills': skill_analysis,
                'metrics': {
                    'skill_count': len(skills),
                    'avg_sentiment': np.mean(sentiment_scores) if sentiment_scores else 0.0,
                    'unique_entities': len(set(
                        entity['entity']
                        for analysis in skill_analysis.values()
                        for entity in analysis['entities']
                    ))
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills section: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_experience_section(self, text: str) -> Dict[str, Any]:
        """Analyze experience section with AI."""
        try:
            # Extract entities
            entities = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.ner_analyzer,
                text
            )
            
            # Group entities by type
            entity_groups = {}
            for entity in entities:
                entity_type = entity['entity']
                if entity_type not in entity_groups:
                    entity_groups[entity_type] = []
                entity_groups[entity_type].append(entity['word'])
                
            # Analyze sentiment
            sentiment = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.sentiment_analyzer,
                text
            )[0]
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text)
            
            return {
                'entities': entity_groups,
                'sentiment': sentiment,
                'key_phrases': key_phrases,
                'metrics': {
                    'entity_count': len(entities),
                    'entity_types': len(entity_groups),
                    'key_phrase_count': len(key_phrases)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing experience section: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_education_section(self, text: str) -> Dict[str, Any]:
        """Analyze education section with AI."""
        try:
            # Extract entities
            entities = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.ner_analyzer,
                text
            )
            
            # Group by education-related entities
            education_entities = {
                'ORG': [],  # Organizations/Institutions
                'DATE': [],  # Dates
                'GPE': [],  # Locations
                'MISC': []  # Other relevant entities
            }
            
            for entity in entities:
                if entity['entity'] in education_entities:
                    education_entities[entity['entity']].append(entity['word'])
                    
            # Extract degrees and certifications
            degrees = await self._extract_degrees(text)
            
            return {
                'entities': education_entities,
                'degrees': degrees,
                'metrics': {
                    'institution_count': len(education_entities['ORG']),
                    'degree_count': len(degrees),
                    'location_count': len(education_entities['GPE'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing education section: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_general_section(self, text: str) -> Dict[str, Any]:
        """Analyze general section with AI."""
        try:
            # Extract entities
            entities = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.ner_analyzer,
                text
            )
            
            # Analyze sentiment
            sentiment = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.sentiment_analyzer,
                text
            )[0]
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text)
            
            return {
                'entities': entities,
                'sentiment': sentiment,
                'key_phrases': key_phrases,
                'metrics': {
                    'entity_count': len(entities),
                    'key_phrase_count': len(key_phrases)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing general section: {str(e)}")
            return {'error': str(e)}
            
    async def _analyze_overall(self, content: str) -> Dict[str, Any]:
        """Perform overall analysis of content."""
        try:
            # Analyze sentiment
            sentiment = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.sentiment_analyzer,
                content
            )[0]
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(content)
            
            # Extract entities
            entities = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.ner_analyzer,
                content
            )
            
            # Group entities by type
            entity_groups = {}
            for entity in entities:
                entity_type = entity['entity']
                if entity_type not in entity_groups:
                    entity_groups[entity_type] = []
                entity_groups[entity_type].append(entity['word'])
                
            return {
                'sentiment': sentiment,
                'key_phrases': key_phrases,
                'entities': entity_groups,
                'metrics': {
                    'entity_count': len(entities),
                    'entity_types': len(entity_groups),
                    'key_phrase_count': len(key_phrases)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in overall analysis: {str(e)}")
            return {'error': str(e)}
            
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        try:
            # Tokenize text
            tokens = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Get BERT embeddings
            with torch.no_grad():
                outputs = self.bert_model(**tokens)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Convert to numpy
            embeddings = embeddings.cpu().numpy()
            
            # Use embeddings to identify important phrases
            # This is a simplified version - you might want to use a more sophisticated approach
            sentences = text.split('.')
            sentence_embeddings = []
            
            for sentence in sentences:
                if sentence.strip():
                    sentence_tokens = self.tokenizer(
                        sentence,
                        return_tensors='pt',
                        truncation=True,
                        max_length=128
                    ).to(self.device)
                    
                    with torch.no_grad():
                        sentence_outputs = self.bert_model(**sentence_tokens)
                        sentence_embedding = sentence_outputs.last_hidden_state.mean(dim=1)
                        sentence_embeddings.append(sentence_embedding.cpu().numpy())
                        
            # Compute similarities
            similarities = []
            for sentence_embedding in sentence_embeddings:
                similarity = np.dot(embeddings, sentence_embedding.T) / (
                    np.linalg.norm(embeddings) * np.linalg.norm(sentence_embedding)
                )
                similarities.append(float(similarity[0][0]))
                
            # Get top phrases
            top_indices = np.argsort(similarities)[-5:]  # Get top 5 phrases
            key_phrases = [
                sentences[i].strip()
                for i in top_indices
                if similarities[i] > 0.5  # Threshold for key phrases
            ]
            
            return key_phrases
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {str(e)}")
            return []
            
    async def _extract_degrees(self, text: str) -> List[str]:
        """Extract degrees and certifications from text."""
        try:
            # Common degree patterns
            degree_patterns = [
                r'\b(?:Bachelor|Master|PhD|Doctorate|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech|M\.?Tech)\b',
                r'\b(?:Associate|Diploma|Certificate|Certification|License)\b',
                r'\b(?:MBA|MD|JD|LLB|LLM|DDS|DMD|DVM|DO|PharmD)\b'
            ]
            
            # Find matches
            degrees = []
            for pattern in degree_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    degrees.append(context)
                    
            return list(dict.fromkeys(degrees))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting degrees: {str(e)}")
            return []
            
    async def match_with_ai(
        self,
        job_description: str,
        candidate_profiles: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Match profiles with AI-enhanced analysis."""
        try:
            # Get base matches
            matches = await self.matching_engine.match_profiles(
                job_description,
                candidate_profiles,
                weights
            )
            
            # Add AI analysis
            for match in matches:
                if 'analysis' in match:
                    # Perform AI analysis
                    ai_analysis = await self.analyze_content(
                        match['analysis'].get('content', '')
                    )
                    match['ai_analysis'] = ai_analysis
                    
            return matches
            
        except Exception as e:
            logger.error(f"Error in match_with_ai: {str(e)}")
            raise
            
    def __del__(self):
        """Cleanup resources."""
        try:
            self.executor.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Error shutting down executor: {str(e)}")
            
    def match_with_ai_enhancement(
        self,
        job_data: Dict[str, Any],
        profile_data: Dict[str, Any],
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Perform matching with optional AI enhancement.
        
        Args:
            job_data: Job description data
            profile_data: Candidate profile data
            use_ai: Whether to use AI-enhanced matching
            
        Returns:
            Dictionary containing match results with AI analysis if enabled
        """
        # Get standard matching results
        standard_results = self.matching_engine.match(job_data, profile_data)
        
        if not use_ai:
            return standard_results
            
        try:
            # Get AI-enhanced analysis
            ai_analysis = self.analyze_content(
                job_data.get('analysis', {}).get('content', '')
            )
            
            # Combine results
            enhanced_results = {
                **standard_results,
                "ai_analysis": ai_analysis
            }
            
            # Adjust match score based on AI analysis
            if ai_analysis.get('sentiment', 0) > 0.5:
                enhanced_results["match_score"] = 0.8
            else:
                enhanced_results["match_score"] = 0.5
                
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced matching: {str(e)}")
            # Return standard results if AI analysis fails
            return standard_results
            
    def batch_match_with_ai(
        self,
        jobs: List[Dict[str, Any]],
        profiles: List[Dict[str, Any]],
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform batch matching with optional AI enhancement.
        
        Args:
            jobs: List of job descriptions
            profiles: List of candidate profiles
            use_ai: Whether to use AI-enhanced matching
            
        Returns:
            List of match results with AI analysis if enabled
        """
        results = []
        
        for job in jobs:
            for profile in profiles:
                match_result = self.match_with_ai_enhancement(
                    job, profile, use_ai=use_ai
                )
                results.append({
                    "job": job.get("title", "Unknown"),
                    "profile": profile.get("name", "Unknown"),
                    "match_result": match_result
                })
                
        # Sort results by match score
        results.sort(
            key=lambda x: x["match_result"]["match_score"],
            reverse=True
        )
        
        return results
        
    def update_skill_database(self, skills: List[str]):
        """
        Update the AI matcher's skill database.
        
        Args:
            skills: List of skills to add to the database
        """
        try:
            self.matching_engine.update_skill_index(skills)
            logger.info(f"Updated skill database with {len(skills)} skills")
        except Exception as e:
            logger.error(f"Error updating skill database: {str(e)}")
            
    def save_models(self, path: Optional[str] = None):
        """
        Save AI models to disk.
        
        Args:
            path: Optional path to save models to
        """
        try:
            self.matching_engine.save_models(path)
        except Exception as e:
            logger.error(f"Error saving AI models: {str(e)}")
            
    def load_models(self, path: Optional[str] = None):
        """
        Load AI models from disk.
        
        Args:
            path: Optional path to load models from
        """
        try:
            self.matching_engine.load_models(path)
        except Exception as e:
            logger.error(f"Error loading AI models: {str(e)}")
            
    def get_skill_similarities(self, skill: str) -> List[Dict[str, Any]]:
        """
        Get similar skills using AI semantic matching.
        
        Args:
            skill: Skill to find matches for
            
        Returns:
            List of similar skills with similarity scores
        """
        try:
            similar_skills = self.matching_engine.find_similar_skills(skill)
            return [
                {
                    "skill": s,
                    "similarity": self.matching_engine.analyze_skill_similarity(skill, s)
                }
                for s in similar_skills
            ]
        except Exception as e:
            logger.error(f"Error finding similar skills: {str(e)}")
            return []
            
    def analyze_experience(self, experience_text: str) -> Dict[str, Any]:
        """
        Analyze experience description using AI.
        
        Args:
            experience_text: Text describing experience
            
        Returns:
            Dictionary containing AI analysis of experience
        """
        try:
            return self.analyze_content(experience_text)
        except Exception as e:
            logger.error(f"Error analyzing experience: {str(e)}")
            return {
                "years_of_experience": 0,
                "key_responsibilities": [],
                "technical_skills": [],
                "industry_domain": "Unknown",
                "role_complexity": "Unknown"
            } 