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
        return self.model is not None and self.api_key is not None
    
    async def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        language: str = "auto",
        previous_qa_pairs: Optional[List[Dict[str, Any]]] = None,
        use_pro_model: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an answer to a question using Gemini API
        
        Args:
            question: The user's question
            context: Additional context from knowledge base
            language: Preferred response language ('en', 'ar', 'auto')
            previous_qa_pairs: Similar Q&A pairs for context
            use_pro_model: Whether to use the more capable Pro model
        
        Returns:
            Dict containing answer, confidence, and metadata
        """
        if not self.is_connected():
            logger.error("Gemini client not available")
            return None
        
        try:
            # Switch to Pro model if requested
            model_to_use = self.model
            if use_pro_model:
                model_to_use = genai.GenerativeModel(
                    model_name=self.pro_model_name,
                    safety_settings=self.model._safety_settings
                )
            
            # Build context-aware prompt
            prompt = self._build_prompt(question, context, language, previous_qa_pairs)
            
            # Call Gemini API
            start_time = time.time()
            response = await asyncio.to_thread(
                model_to_use.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=0.3,  # Lower temperature for more factual responses
                    top_p=0.8,
                    top_k=40
                )
            )
            
            processing_time = time.time() - start_time
            
            # Check if response was blocked
            if not response.text:
                logger.warning("Gemini response was blocked or empty")
                return {
                    "answer": "I apologize, but I cannot provide an answer to this question at the moment.",
                    "confidence": 0.1,
                    "error": "Response blocked or empty",
                    "model_used": model_to_use.model_name,
                    "processing_time": processing_time
                }
            
            # Parse response
            answer_data = self._parse_response(response.text)
            
            # Add metadata
            answer_data.update({
                "model_used": model_to_use.model_name,
                "processing_time": processing_time,
                "finish_reason": getattr(response, 'finish_reason', None)
            })
            
            return answer_data
            
        except Exception as e:
            logger.error(f"Failed to get answer from Gemini: {e}")
            return None
    
    def _build_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        language: str = "auto",
        previous_qa_pairs: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build a comprehensive prompt for Gemini"""
        
        # Detect language if auto
        if language == "auto":
            language = "ar" if any(char in question for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي') else "en"
        
        # Base system context
        system_context = {
            "en": """You are Syria GPT, an AI assistant specialized in providing accurate, helpful information about Syria. 
You have extensive knowledge about Syrian history, culture, geography, politics, economy, and current events.

Your role is to:
1. Provide accurate, well-researched answers about Syria
2. Be respectful and sensitive to the complex situation in Syria
3. Acknowledge when you don't have specific information
4. Provide balanced perspectives on controversial topics
5. Support your answers with reliable sources when possible

Always respond in a helpful, informative manner while being culturally sensitive.""",
            
            "ar": """أنت Syria GPT، مساعد ذكي متخصص في تقديم معلومات دقيقة ومفيدة حول سوريا.
لديك معرفة واسعة بالتاريخ السوري، الثقافة، الجغرافيا، السياسة، الاقتصاد، والأحداث الجارية.

دورك هو:
1. تقديم إجابات دقيقة ومدروسة حول سوريا
2. كن محترماً وحساساً للوضع المعقد في سوريا
3. اعترف عندما لا تملك معلومات محددة
4. قدم وجهات نظر متوازنة حول المواضيع الخلافية
5. ادعم إجاباتك بمصادر موثوقة عند الإمكان

اجب دائماً بطريقة مفيدة وغنية بالمعلومات مع مراعاة الحساسية الثقافية."""
        }
        
        # Build prompt components
        prompt_parts = [
            system_context.get(language, system_context["en"]),
            "",
            f"Question: {question}",
            ""
        ]
        
        # Add context if available
        if context:
            prompt_parts.extend([
                "Relevant context from knowledge base:",
                context,
                ""
            ])
        
        # Add similar Q&A pairs if available
        if previous_qa_pairs:
            prompt_parts.append("Similar previously answered questions:")
            for i, qa in enumerate(previous_qa_pairs[:3], 1):
                prompt_parts.extend([
                    f"{i}. Q: {qa.get('question', 'N/A')}",
                    f"   A: {qa.get('answer', 'N/A')[:200]}...",
                    ""
                ])
        
        # Instructions for response format
        format_instructions = {
            "en": """Please provide your answer in the following JSON format:
{
    "answer": "Your detailed answer here",
    "confidence": 0.95,
    "sources": ["source1", "source2"],
    "language": "en",
    "question_variants": ["alternative phrasing 1", "alternative phrasing 2"],
    "keywords": ["keyword1", "keyword2", "keyword3"]
}

Make sure your confidence score (0.0 to 1.0) reflects how certain you are about the answer.
Provide ONLY the JSON response, no additional text.""",
            
            "ar": """يرجى تقديم إجابتك بالتنسيق JSON التالي:
{
    "answer": "إجابتك المفصلة هنا",
    "confidence": 0.95,
    "sources": ["مصدر1", "مصدر2"],
    "language": "ar",
    "question_variants": ["صياغة بديلة 1", "صياغة بديلة 2"],
    "keywords": ["كلمة مفتاحية1", "كلمة مفتاحية2", "كلمة مفتاحية3"]
}

تأكد أن درجة الثقة (0.0 إلى 1.0) تعكس مدى يقينك من الإجابة.
قدم استجابة JSON فقط، بدون نص إضافي."""
        }
        
        prompt_parts.extend([
            "",
            format_instructions.get(language, format_instructions["en"])
        ])
        
        return "\\n".join(prompt_parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response"""
        try:
            # Clean up the response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            elif "```" in response_text:
                # Handle plain code blocks
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            else:
                json_text = response_text
            
            # Find JSON object bounds
            start_idx = json_text.find("{")
            end_idx = json_text.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = json_text[start_idx:end_idx]
            
            # Parse JSON
            parsed = json.loads(json_text)
            
            # Validate required fields
            if "answer" not in parsed:
                parsed["answer"] = response_text
            
            # Ensure confidence is within valid range
            if "confidence" in parsed:
                parsed["confidence"] = max(0.0, min(1.0, float(parsed.get("confidence", 0.8))))
            else:
                parsed["confidence"] = 0.8
            
            # Ensure other fields have defaults
            parsed.setdefault("sources", [])
            parsed.setdefault("language", "auto")
            parsed.setdefault("question_variants", [])
            parsed.setdefault("keywords", [])
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            # Return basic response as fallback
            return {
                "answer": response_text,
                "confidence": 0.7,
                "sources": [],
                "language": "auto",
                "question_variants": [],
                "keywords": [],
                "parse_error": str(e)
            }
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return {
                "answer": response_text,
                "confidence": 0.6,
                "sources": [],
                "language": "auto", 
                "question_variants": [],
                "keywords": [],
                "error": str(e)
            }
    
    async def evaluate_answer_quality(
        self,
        question: str,
        answer: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality and relevance of an answer
        
        Args:
            question: The original question
            answer: The answer to evaluate
            context: Additional context used
        
        Returns:
            Quality evaluation metrics
        """
        if not self.is_connected():
            return {"quality_score": 0.5, "error": "Gemini not available"}
        
        evaluation_prompt = f"""
Please evaluate this Q&A pair for quality and relevance:

Question: {question}
Answer: {answer}
{f"Context used: {context}" if context else ""}

Evaluate on these criteria (scale 1-10):
1. Accuracy: How factually correct is the answer?
2. Relevance: How well does it answer the specific question?
3. Completeness: Does it cover all important aspects?
4. Clarity: Is it clear and well-structured?
5. Cultural sensitivity: Is it appropriate for the cultural context?

Respond ONLY with this JSON format:
{{
    "overall_quality": 8.5,
    "accuracy": 9,
    "relevance": 8,
    "completeness": 8,
    "clarity": 9,
    "cultural_sensitivity": 9,
    "feedback": "Brief feedback on strengths and areas for improvement"
}}
"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                evaluation_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.1
                )
            )
            
            if response.text:
                return self._parse_response(response.text)
            else:
                return {"quality_score": 0.5, "error": "Evaluation blocked"}
            
        except Exception as e:
            logger.error(f"Failed to evaluate answer quality: {e}")
            return {"quality_score": 0.5, "error": str(e)}
    
    async def generate_question_variants(
        self,
        original_question: str,
        num_variants: int = 5
    ) -> List[str]:
        """Generate alternative phrasings of a question for better matching"""
        if not self.is_connected():
            return []
        
        prompt = f"""
Generate {num_variants} alternative ways to ask this question, maintaining the same meaning:

Original: {original_question}

Consider different:
- Formality levels
- Word choices
- Sentence structures
- Both English and Arabic if applicable

Return ONLY a JSON array: ["variant1", "variant2", "variant3", ...]
No additional text or explanation.
"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7
                )
            )
            
            if not response.text:
                return []
            
            response_text = response.text.strip()
            
            # Extract JSON array
            if response_text.startswith("[") and response_text.endswith("]"):
                return json.loads(response_text)
            else:
                # Try to find JSON array in response
                import re
                json_match = re.search(r'\\[.*\\]', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate question variants: {e}")
            return []
    
    async def check_content_safety(self, text: str) -> Dict[str, Any]:
        """Check if content is safe using Gemini's safety features"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                f"Analyze this text for safety concerns: {text}",
                generation_config=genai.types.GenerationConfig(max_output_tokens=100)
            )
            
            safety_ratings = getattr(response, 'safety_ratings', [])
            
            return {
                "is_safe": bool(response.text),
                "safety_ratings": [
                    {
                        "category": rating.category.name,
                        "probability": rating.probability.name
                    } for rating in safety_ratings
                ] if safety_ratings else []
            }
            
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return {"is_safe": True, "error": str(e)}

# Global Gemini service instance
gemini_service = GeminiService()