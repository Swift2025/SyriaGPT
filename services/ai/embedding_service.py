import os
import logging
from typing import List, Optional, Union
import asyncio
import numpy as np
import hashlib

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Simplified embedding service that generates basic embeddings.
    This is a temporary solution until we resolve the Google API issues.
    """
    
    def __init__(self):
        self.embedding_dimension = 768  # Standard dimension
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        logger.info("Simplified embedding service initialized")
    
    async def generate_embedding(
        self, 
        text: Union[str, List[str]], 
        use_gemini_fallback: bool = True
    ) -> Optional[Union[List[float], List[List[float]]]]:
        """
        Generate basic embeddings for text(s).
        
        Args:
            text: Single text string or list of texts
            use_gemini_fallback: Not used in simplified version
            
        Returns:
            Single embedding vector or list of embeddings
        """
        if not text:
            return None
        
        # Normalize input
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        try:
            embeddings = []
            for text_item in texts:
                # Generate a simple hash-based embedding
                embedding = self._generate_simple_embedding(text_item)
                embeddings.append(embedding)
            
            return embeddings[0] if is_single else embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate a simple embedding based on text hash"""
        try:
            # Create a hash of the text
            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            
            # Convert hash to a list of floats
            embedding = []
            for i in range(0, len(text_hash), 2):
                if len(embedding) >= self.embedding_dimension:
                    break
                hex_pair = text_hash[i:i+2]
                float_val = float(int(hex_pair, 16)) / 255.0  # Normalize to 0-1
                embedding.append(float_val)
            
            # Pad or truncate to exact dimension
            while len(embedding) < self.embedding_dimension:
                embedding.append(0.0)
            
            return embedding[:self.embedding_dimension]
            
        except Exception as e:
            logger.error(f"Simple embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        return self.embedding_dimension
    
    async def compute_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0
    
    async def generate_question_variants(
        self, 
        original_question: str, 
        num_variants: int = 3
    ) -> List[str]:
        """
        Generate variants of a question for better matching.
        This is a simple implementation.
        """
        variants = []
        
        # Simple rule-based variants for Arabic and English
        if any(char in original_question for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي'):
            # Arabic question
            variants.extend([
                f"ما هو {original_question}",
                f"أخبرني عن {original_question}",
                f"شرح {original_question}",
            ])
        else:
            # English question
            variants.extend([
                f"What is {original_question}?",
                f"Tell me about {original_question}",
                f"Explain {original_question}",
            ])
        
        return variants[:num_variants]

# Global embedding service instance
embedding_service = EmbeddingService()