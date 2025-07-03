"""
Explainability module for Resume Matching Engine (RME)
Provides SHAP and LIME explanations for match scores.

Note: SHAP and LIME are optional dependencies. Install them with:
    pip install shap lime
"""

import numpy as np
from typing import Any, Dict, List, Optional

# Optional: SHAP and LIME imports (require installation)
try:
    import shap  # type: ignore  # Optional dependency
    from lime.lime_text import LimeTextExplainer  # type: ignore  # Optional dependency
except ImportError:
    shap = None
    LimeTextExplainer = None

class MatchExplainability:
    """
    Provides explainability for the matching engine using SHAP and LIME.
    """
    def __init__(self, model, tokenizer=None):
        """
        Args:
            model: The embedding or scoring model used for matching.
            tokenizer: Optional tokenizer for text inputs.
        """
        self.model = model
        self.tokenizer = tokenizer

    def explain_with_shap(self, text: str, background_texts: Optional[List[str]]) -> Optional[Any]:
        """
        Generate SHAP explanation for a given text input.
        Args:
            text: The input text to explain.
            background_texts: List of background texts for SHAP explainer.
        Returns:
            SHAP explanation object or None if SHAP is not installed.
        Raises:
            ImportError: If SHAP is not installed.
        """
        if shap is None:
            raise ImportError("SHAP is not installed. Run 'pip install shap' to use this feature.")
        if not background_texts:
            raise ValueError("background_texts must be a non-empty list of strings.")
        # Example: Use KernelExplainer for text embeddings
        def embedding_fn(texts):
            # Convert texts to embeddings using the model
            return np.array([self.model.encode(t) for t in texts])
        explainer = shap.KernelExplainer(embedding_fn, background_texts)
        shap_values = explainer.shap_values([text])
        return shap_values

    def explain_with_lime(self, text: str, class_names: Optional[List[str]] = None) -> Optional[Any]:
        """
        Generate LIME explanation for a given text input.
        Args:
            text: The input text to explain.
            class_names: Optional list of class names for LIME.
        Returns:
            LIME explanation object or None if LIME is not installed.
        Raises:
            ImportError: If LIME is not installed.
        """
        if LimeTextExplainer is None:
            raise ImportError("LIME is not installed. Run 'pip install lime' to use this feature.")
        explainer = LimeTextExplainer(class_names=class_names)
        # Example: Use model's predict_proba or similar for LIME
        def predict_proba(texts):
            # Dummy: Return similarity to a reference (to be replaced)
            return np.array([[self.model.similarity(text, t)] for t in texts])
        exp = explainer.explain_instance(text, predict_proba, num_features=10)
        return exp

    # Placeholder for attention heatmap support
    def explain_with_attention(self, text: str) -> Dict[str, Any]:
        """
        Generate attention heatmap for a given text input (if supported by model).
        Args:
            text: The input text to explain.
        Returns:
            Dictionary with attention weights or visualization data.
        """
        # To be implemented for transformer models with attention
        return {"attention": None, "note": "Attention visualization not yet implemented."} 