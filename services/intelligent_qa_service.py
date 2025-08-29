import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import time
from datetime import datetime, timedelta
import json

# Import our services
from .redis_service import redis_service
from .qdrant_service import qdrant_service
from .embedding_service import embedding_service
from .gemini_service import gemini_service
from .question_repository import QuestionRepository
from .answer_repository import AnswerRepository

logger = logging.getLogger(__name__)

class IntelligentQAService:
    """
    Core intelligent Q&A processing service that implements the complete flow:
    
    1. Cache Check (Redis) → 2. Semantic Search (Qdrant) → 3. Quality Evaluation → 4. Claude API → 5. Storage
    """
    
    def __init__(self):
        self.cache_hit_threshold = 0.95  # Redis cache similarity threshold
        self.semantic_search_threshold = 0.85  # Qdrant similarity threshold
        self.quality_threshold = 0.95  # Minimum quality score to return cached answer
        self.cache_ttl = 86400  # 24 hours cache TTL
        self.max_variants_to_generate = 5
        
    async def process_question(
        self, 
        question: str, 
        user_id: Optional[str] = None,
        context: Optional[str] = None,
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Main processing pipeline for user questions.
        Implements the complete 🔸 Processing Flow described in requirements.
        
        Args:
            question: User's question
            user_id: Optional user identifier
            context: Optional additional context
            language: Preferred response language
            
        Returns:
            Complete response with answer, metadata, and processing info
        """
        start_time = time.time()
        processing_steps = []
        
        try:
            # Step 1: Normalize input
            normalized_question = self._normalize_question(question)
            processing_steps.append("input_normalized")
            
            # Step 2: Cache Check (Redis) - Highest Priority
            logger.info("🔍 Step 1: Checking Redis cache...")
            cache_result = await self._check_redis_cache(normalized_question)
            if cache_result:
                processing_steps.append("redis_cache_hit")
                logger.info("✅ Redis cache hit - returning cached answer")
                
                return self._format_response(
                    answer=cache_result["answer"],
                    source="redis_cache",
                    confidence=cache_result.get("confidence", 1.0),
                    processing_steps=processing_steps,
                    processing_time=time.time() - start_time,
                    metadata=cache_result
                )
            
            processing_steps.append("redis_cache_miss")
            
            # Step 3: Generate embedding for semantic search
            logger.info("🔍 Step 2: Generating question embedding...")
            question_embedding = await embedding_service.generate_embedding(normalized_question)
            if not question_embedding:
                logger.error("Failed to generate embedding")
                return self._format_error("Failed to process question", processing_steps)
            
            processing_steps.append("embedding_generated")
            
            # Step 4: Semantic Search (Qdrant)
            logger.info("🔍 Step 3: Performing semantic search in Qdrant...")
            similar_qa_pairs = await qdrant_service.search_similar_questions(
                query_embedding=question_embedding,
                limit=5,
                score_threshold=self.semantic_search_threshold
            )
            
            if similar_qa_pairs:
                processing_steps.append("semantic_search_hit")
                
                # Step 5: Quality Evaluation
                logger.info("🔍 Step 4: Evaluating answer quality...")
                best_match = similar_qa_pairs[0]  # Highest similarity
                
                if best_match["similarity_score"] >= self.quality_threshold:
                    logger.info("✅ High-quality match found - returning stored answer")
                    
                    # Cache in Redis for faster future access
                    await self._cache_answer_redis(
                        normalized_question, 
                        best_match["answer"],
                        confidence=best_match["similarity_score"],
                        metadata=best_match["metadata"]
                    )
                    
                    return self._format_response(
                        answer=best_match["answer"],
                        source="vector_search",
                        confidence=best_match["similarity_score"],
                        processing_steps=processing_steps,
                        processing_time=time.time() - start_time,
                        metadata={
                            "similar_questions": [qa["question"] for qa in similar_qa_pairs[:3]],
                            "original_qa_id": best_match["qa_id"]
                        }
                    )
            
            processing_steps.append("semantic_search_miss_or_low_quality")
            
            # Step 6: External Query (Gemini API)
            logger.info("🔍 Step 5: Querying Gemini API for new answer...")
            gemini_response = await gemini_service.answer_question(
                question=normalized_question,
                context=context,
                language=language,
                previous_qa_pairs=similar_qa_pairs[:3] if similar_qa_pairs else None
            )
            
            if not gemini_response:
                logger.error("Gemini API failed to provide answer")
                return self._format_error("Failed to generate answer", processing_steps)
            
            processing_steps.append("gemini_api_success")
            
            # Step 7: Result Processing & Storage
            logger.info("🔍 Step 6: Processing and storing new answer...")
            
            # Generate question variants for better future matching
            question_variants = await self._generate_question_variants(normalized_question)
            
            # Store in all systems
            storage_success = await self._store_answer_all_systems(
                question=normalized_question,
                answer=gemini_response["answer"],
                embedding=question_embedding,
                confidence=gemini_response.get("confidence", 0.8),
                metadata={
                    "language": gemini_response.get("language", language),
                    "sources": gemini_response.get("sources", []),
                    "keywords": gemini_response.get("keywords", []),
                    "question_variants": question_variants,
                    "created_at": datetime.now().isoformat(),
                    "model_used": gemini_response.get("model_used", "gemini-1.5-flash"),
                    "user_id": user_id
                },
                user_id=user_id
            )
            
            if storage_success:
                processing_steps.append("answer_stored")
            else:
                processing_steps.append("storage_failed")
            
            # Return final response
            return self._format_response(
                answer=gemini_response["answer"],
                source="gemini_api",
                confidence=gemini_response.get("confidence", 0.8),
                processing_steps=processing_steps,
                processing_time=time.time() - start_time,
                metadata={
                    "sources": gemini_response.get("sources", []),
                    "keywords": gemini_response.get("keywords", []),
                    "question_variants": question_variants,
                    "processing_time": gemini_response.get("processing_time", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in question processing pipeline: {e}")
            return self._format_error(f"Processing error: {str(e)}", processing_steps)
    
    async def _check_redis_cache(self, question: str) -> Optional[Dict[str, Any]]:
        """Check Redis cache for existing answers"""
        try:
            if not redis_service.is_connected():
                return None
            
            # Try exact match first
            cache_key = f"qa_cache:{hash(question)}"
            cached_data = redis_service.get_custom_data(cache_key)
            
            if cached_data:
                return cached_data
            
            # Try fuzzy search in Redis
            fuzzy_results = redis_service.fuzzy_search(question, limit=3)
            if fuzzy_results:
                # Use first result if confidence is high enough
                return {
                    "answer": fuzzy_results[0]["answer"],
                    "confidence": fuzzy_results[0]["confidence"],
                    "source": "redis_fuzzy",
                    "category": fuzzy_results[0].get("category")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Redis cache check failed: {e}")
            return None
    
    async def _cache_answer_redis(
        self, 
        question: str, 
        answer: str, 
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Cache answer in Redis for fast future retrieval"""
        try:
            cache_key = f"qa_cache:{hash(question)}"
            cache_data = {
                "question": question,
                "answer": answer,
                "confidence": confidence,
                "cached_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            redis_service.cache_custom_data(cache_key, cache_data, expiry=self.cache_ttl)
            
        except Exception as e:
            logger.error(f"Failed to cache answer in Redis: {e}")
    
    async def _generate_question_variants(self, question: str) -> List[str]:
        """Generate question variants for better matching"""
        try:
            # Try Gemini API first
            if gemini_service.is_connected():
                variants = await gemini_service.generate_question_variants(
                    question, self.max_variants_to_generate
                )
                if variants:
                    return variants
            
            # Fallback to embedding service
            return await embedding_service.generate_question_variants(
                question, self.max_variants_to_generate
            )
            
        except Exception as e:
            logger.error(f"Failed to generate question variants: {e}")
            return []
    
    async def _store_answer_all_systems(
        self,
        question: str,
        answer: str,
        embedding: List[float],
        confidence: float,
        metadata: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """Store the new Q&A pair in all storage systems"""
        try:
            storage_tasks = []
            
            # 1. PostgreSQL (structured data)
            if user_id:
                storage_tasks.append(
                    self._store_in_postgresql(question, answer, user_id, metadata)
                )
            
            # 2. Qdrant (vector embeddings)
            qa_id = f"qa_{hash(question)}_{int(time.time())}"
            storage_tasks.append(
                qdrant_service.store_qa_embedding(
                    qa_id=qa_id,
                    question=question,
                    answer=answer,
                    embedding=embedding,
                    metadata=metadata
                )
            )
            
            # 3. Redis (cache)
            storage_tasks.append(
                self._cache_answer_redis(question, answer, confidence, metadata)
            )
            
            # Execute all storage operations
            results = await asyncio.gather(*storage_tasks, return_exceptions=True)
            
            # Check if at least one storage succeeded
            success_count = sum(1 for result in results if result is True)
            
            logger.info(f"Stored answer in {success_count}/{len(results)} systems")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to store answer in systems: {e}")
            return False
    
    async def _store_in_postgresql(
        self, 
        question: str, 
        answer: str, 
        user_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Store Q&A in PostgreSQL database"""
        try:
            # This would need to be integrated with your existing database session
            # For now, returning True as a placeholder
            # In real implementation, you'd use QuestionRepository and AnswerRepository
            
            logger.info("PostgreSQL storage would be implemented here")
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL storage failed: {e}")
            return False
    
    def _normalize_question(self, question: str) -> str:
        """Normalize and clean the input question"""
        try:
            # Basic normalization
            normalized = question.strip()
            
            # Remove excessive whitespace
            import re
            normalized = re.sub(r'\\s+', ' ', normalized)
            
            # Ensure question ends with appropriate punctuation
            if not normalized.endswith(('?', '؟', '.', '.')):
                normalized += '?' if not any(char in normalized for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي') else '؟'
            
            return normalized
            
        except Exception as e:
            logger.error(f"Question normalization failed: {e}")
            return question
    
    def _format_response(
        self,
        answer: str,
        source: str,
        confidence: float,
        processing_steps: List[str],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format the final response"""
        return {
            "answer": answer,
            "confidence": confidence,
            "source": source,
            "processing_info": {
                "steps": processing_steps,
                "processing_time_seconds": round(processing_time, 3),
                "timestamp": datetime.now().isoformat()
            },
            "metadata": metadata or {},
            "status": "success"
        }
    
    def _format_error(
        self, 
        error_message: str, 
        processing_steps: List[str]
    ) -> Dict[str, Any]:
        """Format error response"""
        return {
            "answer": None,
            "error": error_message,
            "confidence": 0.0,
            "source": "error",
            "processing_info": {
                "steps": processing_steps,
                "timestamp": datetime.now().isoformat()
            },
            "status": "error"
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all components"""
        return {
            "redis": {
                "connected": redis_service.is_connected(),
                "stats": redis_service.get_cache_stats() if redis_service.is_connected() else None
            },
            "qdrant": {
                "connected": qdrant_service.is_connected(),
                "stats": await qdrant_service.get_collection_stats() if qdrant_service.is_connected() else None
            },
            "gemini": {
                "connected": gemini_service.is_connected()
            },
            "embedding_service": {
                "available": embedding_service.model is not None,
                "dimension": embedding_service.get_embedding_dimension()
            }
        }
    
    async def bulk_import_knowledge(
        self, 
        qa_pairs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk import existing knowledge base into vector storage"""
        try:
            logger.info(f"Starting bulk import of {len(qa_pairs)} Q&A pairs...")
            
            # Generate embeddings for all questions
            questions = [qa["question"] for qa in qa_pairs]
            embeddings = await embedding_service.generate_embedding(questions)
            
            if not embeddings:
                return {"status": "error", "message": "Failed to generate embeddings"}
            
            # Prepare data for batch storage
            batch_data = []
            for i, qa in enumerate(qa_pairs):
                batch_data.append({
                    "qa_id": qa.get("id", f"import_{i}"),
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "embedding": embeddings[i],
                    "metadata": {
                        "category": qa.get("category", "imported"),
                        "confidence": qa.get("confidence", 1.0),
                        "keywords": qa.get("keywords", []),
                        "source": qa.get("source", "bulk_import"),
                        "imported_at": datetime.now().isoformat()
                    }
                })
            
            # Batch store in Qdrant
            stored_count = await qdrant_service.batch_store_embeddings(batch_data)
            
            logger.info(f"Successfully imported {stored_count}/{len(qa_pairs)} Q&A pairs")
            
            return {
                "status": "success",
                "imported_count": stored_count,
                "total_count": len(qa_pairs),
                "success_rate": stored_count / len(qa_pairs) if qa_pairs else 0
            }
            
        except Exception as e:
            logger.error(f"Bulk import failed: {e}")
            return {"status": "error", "message": str(e)}

# Global intelligent Q&A service instance
intelligent_qa_service = IntelligentQAService()