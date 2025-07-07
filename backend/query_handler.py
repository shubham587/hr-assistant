import logging
from typing import Dict, List, Optional
from vector_store import VectorStore
from llm_service import LLMService

logger = logging.getLogger(__name__)

class QueryHandler:
    def __init__(self, vector_store: VectorStore, llm_service: LLMService):
        self.vector_store = vector_store
        self.llm_service = llm_service
        
    def process_query(self, user_query: str) -> Dict:
        """
        Process user query through the RAG pipeline:
        1. Search for relevant document chunks
        2. Generate response using LLM with context
        3. Format response with sources
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            # Step 1: Search for relevant chunks (reduced to fit context limit)
            relevant_chunks = self.vector_store.search_similar_chunks(
                query=user_query,
                n_results=2
            )
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information in the uploaded documents to answer your question. Please make sure you've uploaded the necessary HR documents.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # Step 2: Generate response using LLM
            response_text = self.llm_service.generate_response(
                query=user_query,
                context_chunks=relevant_chunks
            )
            
            # Step 3: Extract sources from chunks
            sources = self._extract_sources(relevant_chunks)
            
            # Step 4: Determine confidence based on relevance
            confidence = self._calculate_confidence(relevant_chunks)
            
            return {
                "answer": response_text,
                "sources": sources,
                "confidence": confidence,
                "chunks_used": len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I'm experiencing technical difficulties. Please try again later.",
                "sources": [],
                "confidence": "error"
            }
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Extract and format source information from chunks"""
        sources = []
        seen_documents = set()
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            document = metadata.get('document', 'Unknown')
            
            # Avoid duplicate documents
            if document not in seen_documents:
                sources.append({
                    "document": document,
                    "relevance_score": round(1 - chunk.get('distance', 0), 2),
                    "chunk_info": f"Words {metadata.get('start_word', 0)}-{metadata.get('end_word', 0)}"
                })
                seen_documents.add(document)
        
        return sources
    
    def _calculate_confidence(self, chunks: List[Dict]) -> str:
        """Calculate confidence level based on chunk relevance"""
        if not chunks:
            return "low"
        
        # Calculate average distance (lower is better)
        avg_distance = sum(chunk.get('distance', 1) for chunk in chunks) / len(chunks)
        
        if avg_distance < 0.3:
            return "high"
        elif avg_distance < 0.6:
            return "medium"
        else:
            return "low"
    
    def categorize_query(self, query: str) -> str:
        """
        Categorize the query type for better routing
        """
        query_lower = query.lower()
        
        # Benefits related
        if any(keyword in query_lower for keyword in ['benefit', 'insurance', 'health', 'dental', 'vision', 'retirement', '401k']):
            return "benefits"
        
        # Leave related
        if any(keyword in query_lower for keyword in ['vacation', 'leave', 'sick', 'time off', 'holiday', 'pto', 'parental']):
            return "leave"
        
        # Remote work / conduct
        if any(keyword in query_lower for keyword in ['remote', 'work from home', 'dress code', 'conduct', 'policy']):
            return "conduct"
        
        # Compensation
        if any(keyword in query_lower for keyword in ['salary', 'pay', 'compensation', 'raise', 'bonus']):
            return "compensation"
        
        # General onboarding
        if any(keyword in query_lower for keyword in ['onboarding', 'first day', 'new employee', 'orientation']):
            return "onboarding"
        
        return "general"
    
    def search_by_category(self, query: str, category: str) -> List[Dict]:
        """
        Search for documents with category-specific filtering
        This is a placeholder for future enhancement
        """
        # For now, just use regular search
        # In future, we could add category metadata to chunks
        return self.vector_store.search_similar_chunks(query, n_results=2)
    
    def get_suggested_questions(self) -> List[str]:
        """
        Return a list of suggested questions based on common HR topics
        """
        return [
            "How many vacation days do I get as a new employee?",
            "What's the process for requesting sick leave?",
            "Can I work remotely and what are the guidelines?",
            "How do I enroll in health insurance?",
            "What are the company holidays?",
            "How do I request time off?",
            "What's the dress code policy?",
            "When do I get my first performance review?",
            "How does the 401k plan work?",
            "What should I do on my first day?"
        ]
    
    def validate_query(self, query: str) -> Dict:
        """
        Validate if the query is appropriate for HR assistant
        """
        if not query or len(query.strip()) < 3:
            return {
                "valid": False,
                "message": "Please provide a more detailed question."
            }
        
        # Check for very long queries
        if len(query) > 500:
            return {
                "valid": False,
                "message": "Please keep your question under 500 characters."
            }
        
        # Check for inappropriate content (basic check)
        inappropriate_keywords = ['hack', 'exploit', 'illegal', 'inappropriate']
        if any(keyword in query.lower() for keyword in inappropriate_keywords):
            return {
                "valid": False,
                "message": "Please ask questions related to HR policies and procedures."
            }
        
        return {
            "valid": True,
            "message": "Query is valid"
        }
    
    def get_system_status(self) -> Dict:
        """
        Get status of all system components
        """
        return {
            "vector_store": self.vector_store.is_healthy(),
            "llm_service": self.llm_service.is_healthy(),
            "collection_stats": self.vector_store.get_collection_stats()
        } 