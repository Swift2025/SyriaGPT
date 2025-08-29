import os
import logging
from typing import List, Optional, Union
import asyncio
from sentence_transformers import SentenceTransformer
import numpy as np
import google.generativeai as genai
from google.cloud import aiplatform

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating text embeddings using multiple providers.
    Supports multilingual text (English and Arabic).
    """
    
    def __init__(self):
        self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"  # Supports Arabic
        self.model: Optional[SentenceTransformer] = None
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.embedding_dimension = 384  # Dimension for the multilingual model
        self.gemini_embedding_dimension = 768  # Dimension for Gemini embeddings
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models"""
        try:
            # Initialize SentenceTransformer (primary)
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"SentenceTransformer model '{self.model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            self.model = None
        
        # Initialize Gemini as fallback
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GEMINI_API_KEY not found, Gemini embeddings unavailable")
    
    async def generate_embedding(
        self, 
        text: Union[str, List[str]], 
        use_gemini_fallback: bool = True
    ) -> Optional[Union[List[float], List[List[float]]]]:
        """
        Generate embeddings for text(s). Supports both single text and batch processing.
        
        Args:
            text: Single text string or list of texts
            use_gemini_fallback: Whether to use Gemini if SentenceTransformer fails
            
        Returns:
            Single embedding vector or list of embeddings
        """
        if not text:
            return None
        
        # Normalize input
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        # Try SentenceTransformer first
        if self.model:
            try:
                embeddings = await self._generate_sentence_transformer_embeddings(texts)
                if embeddings is not None:
                    return embeddings[0] if is_single else embeddings
            except Exception as e:
                logger.error(f"SentenceTransformer failed: {e}")
        
        # Fallback to Gemini
        if use_gemini_fallback and self.gemini_api_key:
            try:
                embeddings = await self._generate_gemini_embeddings(texts)
                if embeddings is not None:
                    return embeddings[0] if is_single else embeddings
            except Exception as e:
                logger.error(f"Gemini embeddings failed: {e}")
        
        logger.error("All embedding methods failed")
        return None
    
    async def _generate_sentence_transformer_embeddings(
        self, 
        texts: List[str]
    ) -> Optional[List[List[float]]]:
        """Generate embeddings using SentenceTransformer"""
        if not self.model:
            return None
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                texts
            )
            
            # Convert numpy arrays to lists
            return [embedding.tolist() for embedding in embeddings]
            
        except Exception as e:
            logger.error(f"SentenceTransformer embedding generation failed: {e}")
            return None
    
    async def _generate_gemini_embeddings(
        self, 
        texts: List[str]
    ) -> Optional[List[List[float]]]:
        """Generate embeddings using Gemini as fallback"""
        if not self.gemini_api_key:
            return None
        
        try:
            embeddings = []
            
            for text in texts:
                # Use Gemini's embedding model
                response = await asyncio.to_thread(
                    genai.embed_content,
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                
                embeddings.append(response['embedding'])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {e}")
            return None
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        if self.model:
            return self.embedding_dimension
        return self.gemini_embedding_dimension  # Gemini embedding dimension
    
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
        This is a simple implementation - can be enhanced with LLMs.
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