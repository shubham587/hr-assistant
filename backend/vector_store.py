import os
# Disable ChromaDB telemetry before importing
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import chromadb
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with telemetry disabled
            self.client = chromadb.PersistentClient(
                path="../data/chroma_db",
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="hr_documents",
                metadata={"description": "HR document embeddings"}
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_document_chunks(self, chunks: List[Dict], document_name: str) -> bool:
        """Add document chunks to vector store"""
        try:
            if not chunks:
                logger.warning("No chunks to add")
                return False
            
            # Prepare data for ChromaDB
            texts = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_name}_{i}"
                texts.append(chunk['text'])
                metadatas.append({
                    'document': document_name,
                    'chunk_id': chunk['chunk_id'],
                    'word_count': chunk['word_count'],
                    'start_word': chunk['start_word'],
                    'end_word': chunk['end_word']
                })
                ids.append(chunk_id)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks from {document_name} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {str(e)}")
            return False
    
    def search_similar_chunks(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar chunks based on query"""
        try:
            if not self.collection:
                logger.error("Vector store not initialized")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def search_by_document(self, document_name: str, query: str, n_results: int = 3) -> List[Dict]:
        """Search for chunks within a specific document"""
        try:
            if not self.collection:
                logger.error("Vector store not initialized")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search with document filter
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where={"document": document_name}
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching by document: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            if not self.collection:
                return {"error": "Vector store not initialized"}
            
            count = self.collection.count()
            return {
                "total_chunks": count,
                "status": "healthy" if count > 0 else "empty"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if vector store is healthy"""
        try:
            return self.client is not None and self.collection is not None
        except:
            return False
    
    def clear_collection(self):
        """Clear all documents from collection (for testing)"""
        try:
            if self.collection:
                # Get all IDs
                results = self.collection.get()
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
                logger.info("Cleared all documents from vector store")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
    
    def delete_document(self, document_name: str):
        """Delete all chunks for a specific document"""
        try:
            if not self.collection:
                logger.error("Vector store not initialized")
                return
            
            # Get all chunks for this document
            results = self.collection.get(where={"document": document_name})
            
            if results['ids']:
                # Delete all chunks for this document
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_name}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}") 