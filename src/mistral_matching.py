"""
Mistral AI Integration for RME
Uses Mistral Magistral-Small-2506 model for enhanced matching capabilities.
"""

import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from .matching_engine import MatchingEngine

logger = logging.getLogger(__name__)

class MistralMatchingEngine(MatchingEngine):
    """Enhanced matching engine using Mistral AI Magistral-Small-2506."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_path: str = "models/mistral",
        device: Optional[str] = None,
        max_workers: int = 4,
        cache_size: int = 1000
    ):
        """Initialize the Mistral matching engine."""
        super().__init__(config, model_path, device, max_workers, cache_size)
        self.model_name = "mistralai/Magistral-Small-2506"
        self._load_mistral_model()
        
    def _load_mistral_model(self) -> None:
        """Load Mistral model and tokenizer."""
        try:
            logger.info("Loading Mistral AI model...")
            
            # Set device
            self.device = self.device or ('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {self.device}")
            
            # Create model directory if it doesn't exist
            model_dir = Path(self.model_path) / "mistral"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=str(model_dir),
                local_files_only=False  # Allow remote download if not found locally
            )
            
            self.mistral_model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=str(model_dir),
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map="auto" if self.device == 'cuda' else None,
                local_files_only=False  # Allow remote download if not found locally
            )
            
            # Move model to device if not using device_map
            if self.device != 'cuda':
                self.mistral_model = self.mistral_model.to(self.device)
            
            logger.info("Successfully loaded Mistral AI model.")
            
        except Exception as e:
            logger.warning(f"Mistral model not found locally. Attempting to download. This might take some time depending on your network speed.")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    cache_dir=str(model_dir),
                    local_files_only=False # Re-attempt download
                )
                self.mistral_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    cache_dir=str(model_dir),
                    torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                    device_map="auto" if self.device == 'cuda' else None,
                    local_files_only=False # Re-attempt download
                )
                logger.info("Successfully downloaded and loaded Mistral AI model.")
            except Exception as download_e:
                logger.error(f"Error downloading Mistral model: {str(download_e)}")
                raise # Re-raise original error if download also fails
            
    def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings using Mistral model."""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Get model outputs
            with torch.no_grad():
                outputs = self.mistral_model(**inputs, output_hidden_states=True)
                
            # Use last hidden state as embedding
            last_hidden = outputs.hidden_states[-1]
            
            # Mean pooling
            attention_mask = inputs['attention_mask'].unsqueeze(-1)
            embeddings = (last_hidden * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
            
            return embeddings.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return np.zeros((1, 4096))  # Return zero vector as fallback
            
    def match(self, job_description: str, candidate_profile: str) -> Dict[str, Any]:
        """Enhanced matching using Mistral AI."""
        try:
            # Get base matching results
            base_results = super().match(job_description, candidate_profile)
            
            # Generate Mistral embeddings
            job_embedding = self._generate_embeddings(job_description)
            profile_embedding = self._generate_embeddings(candidate_profile)
            
            # Calculate semantic similarity
            similarity = np.dot(job_embedding, profile_embedding.T) / (
                np.linalg.norm(job_embedding) * np.linalg.norm(profile_embedding)
            )
            
            # Enhance base results with Mistral insights
            enhanced_results = {
                **base_results,
                'mistral_score': float(similarity[0][0]),
                'enhanced_score': (base_results['score'] + float(similarity[0][0])) / 2,
                'model_version': 'mistral-magistral-small-2506',
                'processing_details': {
                    'model': self.model_name,
                    'device': self.device,
                    'embedding_dim': job_embedding.shape[1]
                }
            }
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in Mistral matching: {str(e)}")
            return {
                'error': str(e),
                'score': 0.0,
                'section_scores': {},
                'matching_skills': [],
                'missing_skills': [],
                'mistral_score': 0.0,
                'enhanced_score': 0.0
            }
            
    def __del__(self):
        """Cleanup resources."""
        try:
            # Clear CUDA cache if using GPU
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            super().__del__()
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}") 