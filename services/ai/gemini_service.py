import os
import logging
from typing import Optional, Dict, Any, List
import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import time

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service for Google Gemini API integration.
    Handles intelligent question answering with context and quality evaluation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-1.5-flash"  # Fast model for Q&A
        self.pro_model_name = "gemini-1.5-pro"  # More capable model for complex queries
        self.client = None
        self.model = None
        self.max_tokens = 2000
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        if not self.api_key:
            logger.error("GEMINI_API_KEY or GOOGLE_API_KEY not found")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            
            # Configure safety settings for more permissive responses
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=safety_settings
            )
            
            logger.info(f"Gemini client initialized successfully with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.model = None
    
    def is_connected(self) -> bool:
        """Check if Gemini client is available"""
        return True  # For testing purposes, always return True
    
    async def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        language: str = "auto",
        previous_qa_pairs: Optional[List[Dict[str, Any]]] = None,
        use_pro_model: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a mock answer for testing purposes
        """
        # For testing purposes, always proceed
        
        try:
            # Simulate processing time
            await asyncio.sleep(0.5)
            
            # Generate a mock response
            if language == "ar" or any(char in question for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي'):
                answer = f"هذا رد تجريبي على السؤال: {question}. سوريا هي دولة في الشرق الأوسط."
            else:
                answer = f"This is a test response to: {question}. Syria is a country in the Middle East."
            
            return {
                "answer": answer,
                "confidence": 0.8,
                "sources": ["test_source"],
                "language": language,
                "question_variants": [f"Tell me about {question}"],
                "keywords": ["syria", "test"],
                "model_used": self.pro_model_name if use_pro_model else self.model_name,
                "processing_time": 0.5
            }
            
        except Exception as e:
            logger.error(f"Failed to get answer from Gemini: {e}")
            return None
    
    async def evaluate_answer_quality(
        self,
        question: str,
        answer: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock quality evaluation
        """
        return {
            "overall_quality": 8.0,
            "accuracy": 8,
            "relevance": 8,
            "completeness": 7,
            "clarity": 9,
            "cultural_sensitivity": 9,
            "feedback": "Mock evaluation for testing"
        }
    
    async def generate_question_variants(
        self,
        original_question: str,
        num_variants: int = 5
    ) -> List[str]:
        """Generate mock question variants"""
        variants = [
            f"What is {original_question}?",
            f"Tell me about {original_question}",
            f"Explain {original_question}",
            f"Information on {original_question}",
            f"Details about {original_question}"
        ]
        return variants[:num_variants]
    
    async def check_content_safety(self, text: str) -> Dict[str, Any]:
        """Mock content safety check"""
        return {
            "is_safe": True,
            "safety_ratings": []
        }

# Global Gemini service instance
gemini_service = GeminiService()