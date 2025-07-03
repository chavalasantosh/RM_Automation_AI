"""
Script to download and prepare Mistral AI model for offline use.
"""

import logging
import os
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_model(
    model_name: str = "mistralai/Magistral-Small-2506",
    output_dir: str = "models/mistral",
    quantize: bool = True
) -> None:
    """Download and prepare Mistral model for offline use."""
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading model {model_name} to {output_path}")
        
        # Set device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device}")
        
        # Download tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=str(output_path)
        )
        tokenizer.save_pretrained(output_path)
        
        # Download model
        logger.info("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=str(output_path),
            torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            device_map="auto" if device == 'cuda' else None
        )
        
        # Quantize model if requested
        if quantize and device == 'cuda':
            logger.info("Quantizing model to 4-bit...")
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=str(output_path),
                quantization_config=quantization_config,
                device_map="auto"
            )
        
        # Save model
        logger.info("Saving model...")
        model.save_pretrained(
            output_path,
            safe_serialization=True
        )
        
        logger.info("Model downloaded and prepared successfully!")
        
        # Print model info
        logger.info(f"Model saved to: {output_path}")
        logger.info(f"Model size: {model.get_memory_footprint() / 1024**2:.2f} MB")
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download Mistral AI model for offline use")
    parser.add_argument(
        "--model",
        default="mistralai/Magistral-Small-2506",
        help="Model name or path"
    )
    parser.add_argument(
        "--output-dir",
        default="models/mistral",
        help="Output directory for model files"
    )
    parser.add_argument(
        "--no-quantize",
        action="store_true",
        help="Disable model quantization"
    )
    
    args = parser.parse_args()
    
    download_model(
        model_name=args.model,
        output_dir=args.output_dir,
        quantize=not args.no_quantize
    )

if __name__ == "__main__":
    main() 