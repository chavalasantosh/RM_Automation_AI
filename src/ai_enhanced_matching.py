import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

class AIEnhancedMatching:
    """
    AI-enhanced matching capabilities using local models.
    This class provides advanced matching features using offline models.
    """
    
    def __init__(self, model_path: str = "models", device: str = None):
        """
        Initialize the AI-enhanced matching system.
        
        Args:
            model_path: Path to store/load models
            device: Device to run models on ('cuda', 'cpu', or None for auto)
        """
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all required models."""
        try:
            # Initialize sentence transformer for semantic matching
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.sentence_model.to(self.device)
            
            # Initialize local LLM for advanced analysis
            # Using a smaller model that can run locally
            model_name = "facebook/opt-125m"  # Small model that can run locally
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.llm_model = AutoModelForCausalLM.from_pretrained(model_name)
            self.llm_model.to(self.device)
            
            # Initialize FAISS index for similarity search
            self.skill_index = faiss.IndexFlatL2(384)  # 384 is the dimension of all-MiniLM-L6-v2
            self.skill_descriptions = []
            
            logger.info("Successfully initialized all models")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise
            
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Analyze semantic similarity between two skills.
        
        Args:
            skill1: First skill
            skill2: Second skill
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Get embeddings for both skills
            embeddings = self.sentence_model.encode([skill1, skill2])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating skill similarity: {str(e)}")
            return 0.0
            
    def analyze_experience_context(self, experience_text: str) -> Dict[str, Any]:
        """
        Analyze experience description using local LLM.
        
        Args:
            experience_text: Text describing experience
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Prepare prompt for the model
            prompt = f"""Analyze the following work experience and extract key information:
            Experience: {experience_text}
            
            Extract:
            1. Years of experience
            2. Key responsibilities
            3. Technical skills used
            4. Industry domain
            5. Role complexity
            
            Format as JSON."""
            
            # Generate analysis
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.llm_model.generate(
                **inputs,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7
            )
            
            # Parse the output
            analysis_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    analysis_json = json.loads(analysis_text[json_start:json_end])
                else:
                    analysis_json = {
                        "years_of_experience": 0,
                        "key_responsibilities": [],
                        "technical_skills": [],
                        "industry_domain": "Unknown",
                        "role_complexity": "Unknown"
                    }
            except json.JSONDecodeError:
                logger.warning("Could not parse LLM output as JSON")
                analysis_json = {
                    "years_of_experience": 0,
                    "key_responsibilities": [],
                    "technical_skills": [],
                    "industry_domain": "Unknown",
                    "role_complexity": "Unknown"
                }
                
            return analysis_json
            
        except Exception as e:
            logger.error(f"Error analyzing experience context: {str(e)}")
            return {
                "years_of_experience": 0,
                "key_responsibilities": [],
                "technical_skills": [],
                "industry_domain": "Unknown",
                "role_complexity": "Unknown"
            }
            
    def find_similar_skills(self, skill: str, threshold: float = 0.7) -> List[str]:
        """
        Find similar skills using semantic search.
        
        Args:
            skill: Skill to find matches for
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar skills
        """
        try:
            # Get embedding for the input skill
            skill_embedding = self.sentence_model.encode([skill])[0]
            
            # Search in FAISS index
            D, I = self.skill_index.search(
                skill_embedding.reshape(1, -1).astype('float32'),
                k=5  # Get top 5 matches
            )
            
            # Filter by threshold and get skill names
            similar_skills = []
            for distance, idx in zip(D[0], I[0]):
                if idx < len(self.skill_descriptions):  # Valid index
                    similarity = 1 - (distance / 2)  # Convert distance to similarity
                    if similarity >= threshold:
                        similar_skills.append(self.skill_descriptions[idx])
                        
            return similar_skills
            
        except Exception as e:
            logger.error(f"Error finding similar skills: {str(e)}")
            return []
            
    def analyze_candidate_fit(self, job_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform advanced analysis of candidate fit using AI models.
        
        Args:
            job_data: Job description data
            profile_data: Candidate profile data
            
        Returns:
            Dictionary containing advanced analysis results
        """
        try:
            analysis = {
                "semantic_skill_matches": [],
                "experience_analysis": {},
                "role_complexity_match": 0.0,
                "industry_fit": 0.0,
                "skill_gap_analysis": [],
                "recommendations": []
            }
            
            # Analyze semantic skill matches
            for job_skill in job_data.get('required_skills', []):
                best_match_score = 0.0
                best_match = None
                
                for profile_skill in profile_data.get('skills', []):
                    similarity = self.analyze_skill_similarity(job_skill, profile_skill)
                    if similarity > best_match_score:
                        best_match_score = similarity
                        best_match = profile_skill
                        
                if best_match_score >= 0.7:  # Good match threshold
                    analysis["semantic_skill_matches"].append({
                        "job_skill": job_skill,
                        "profile_skill": best_match,
                        "similarity": best_match_score
                    })
                    
            # Analyze experience context
            if 'experience' in profile_data:
                exp_analysis = self.analyze_experience_context(profile_data['experience'])
                analysis["experience_analysis"] = exp_analysis
                
                # Calculate role complexity match
                if 'role_complexity' in exp_analysis:
                    complexity_levels = {
                        "Entry": 1,
                        "Junior": 2,
                        "Mid": 3,
                        "Senior": 4,
                        "Lead": 5,
                        "Architect": 6
                    }
                    profile_complexity = complexity_levels.get(
                        exp_analysis["role_complexity"], 3
                    )
                    job_complexity = complexity_levels.get(
                        job_data.get("role_level", "Mid"), 3
                    )
                    analysis["role_complexity_match"] = 1 - abs(
                        profile_complexity - job_complexity
                    ) / 5.0
                    
            # Generate recommendations
            if analysis["semantic_skill_matches"]:
                missing_skills = set(job_data.get('required_skills', [])) - set(
                    m["job_skill"] for m in analysis["semantic_skill_matches"]
                )
                if missing_skills:
                    analysis["skill_gap_analysis"] = list(missing_skills)
                    analysis["recommendations"].append(
                        f"Consider developing skills in: {', '.join(missing_skills)}"
                    )
                    
            # Add experience recommendations
            if analysis["experience_analysis"].get("years_of_experience", 0) < job_data.get("required_experience", 0):
                analysis["recommendations"].append(
                    "Consider gaining more experience in the required domain"
                )
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error in advanced candidate analysis: {str(e)}")
            return {
                "semantic_skill_matches": [],
                "experience_analysis": {},
                "role_complexity_match": 0.0,
                "industry_fit": 0.0,
                "skill_gap_analysis": [],
                "recommendations": ["Error in analysis"]
            }
            
    def update_skill_index(self, skills: List[str]):
        """
        Update the FAISS index with new skills.
        
        Args:
            skills: List of skills to add to the index
        """
        try:
            # Get embeddings for all skills
            embeddings = self.sentence_model.encode(skills)
            
            # Add to FAISS index
            self.skill_index.add(embeddings.astype('float32'))
            
            # Update skill descriptions
            self.skill_descriptions.extend(skills)
            
            logger.info(f"Updated skill index with {len(skills)} new skills")
            
        except Exception as e:
            logger.error(f"Error updating skill index: {str(e)}")
            
    def save_models(self, path: Optional[str] = None):
        """
        Save models to disk.
        
        Args:
            path: Optional path to save models to
        """
        try:
            save_path = Path(path) if path else self.model_path
            
            # Save sentence transformer
            self.sentence_model.save(str(save_path / "sentence_transformer"))
            
            # Save LLM model and tokenizer
            self.llm_model.save_pretrained(str(save_path / "llm_model"))
            self.tokenizer.save_pretrained(str(save_path / "llm_model"))
            
            # Save FAISS index
            faiss.write_index(self.skill_index, str(save_path / "skill_index.faiss"))
            
            # Save skill descriptions
            with open(save_path / "skill_descriptions.json", "w") as f:
                json.dump(self.skill_descriptions, f)
                
            logger.info(f"Successfully saved all models to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            
    def load_models(self, path: Optional[str] = None):
        """
        Load models from disk.
        
        Args:
            path: Optional path to load models from
        """
        try:
            load_path = Path(path) if path else self.model_path
            
            # Load sentence transformer
            self.sentence_model = SentenceTransformer(str(load_path / "sentence_transformer"))
            self.sentence_model.to(self.device)
            
            # Load LLM model and tokenizer
            self.llm_model = AutoModelForCausalLM.from_pretrained(str(load_path / "llm_model"))
            self.tokenizer = AutoTokenizer.from_pretrained(str(load_path / "llm_model"))
            self.llm_model.to(self.device)
            
            # Load FAISS index
            self.skill_index = faiss.read_index(str(load_path / "skill_index.faiss"))
            
            # Load skill descriptions
            with open(load_path / "skill_descriptions.json", "r") as f:
                self.skill_descriptions = json.load(f)
                
            logger.info(f"Successfully loaded all models from {load_path}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            # Re-initialize models if loading fails
            self._initialize_models() 