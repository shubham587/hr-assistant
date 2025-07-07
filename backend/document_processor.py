import PyPDF2
import json
import os
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 500  # Reduced for better context management
        self.chunk_overlap = 100
        
    def process_pdf(self, file_path: str) -> bool:
        """
        Process a PDF file: extract text, create chunks, and store them
        """
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(file_path)
            if not text.strip():
                logger.error(f"No text extracted from {file_path}")
                return False
            
            # Create chunks
            chunks = self._create_chunks(text)
            
            # Save chunks to JSON file
            filename = os.path.basename(file_path)
            self._save_chunks(chunks, filename)
            
            # Add to vector store
            from vector_store import VectorStore
            vector_store = VectorStore()
            vector_store.add_document_chunks(chunks, filename)
            
            logger.info(f"Successfully processed {filename} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return False
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text
                        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        
        # Fix common PDF extraction issues
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        
        return text.strip()
    
    def _create_chunks(self, text: str) -> List[Dict]:
        """Create text chunks with overlap"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text,
                    'chunk_id': len(chunks),
                    'word_count': len(chunk_words),
                    'start_word': i,
                    'end_word': i + len(chunk_words)
                })
        
        return chunks
    
    def _save_chunks(self, chunks: List[Dict], filename: str):
        """Save chunks to JSON file"""
        try:
            chunks_filename = f"{filename}_chunks.json"
            chunks_path = os.path.join('../data/chunks', chunks_filename)
            
            with open(chunks_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'document': filename,
                    'chunks': chunks,
                    'total_chunks': len(chunks)
                }, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(chunks)} chunks to {chunks_path}")
            
        except Exception as e:
            logger.error(f"Error saving chunks: {str(e)}")
    
    def get_document_chunks(self, filename: str) -> List[Dict]:
        """Load chunks from JSON file"""
        try:
            chunks_filename = f"{filename}_chunks.json"
            chunks_path = os.path.join('../data/chunks', chunks_filename)
            
            if os.path.exists(chunks_path):
                with open(chunks_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('chunks', [])
            
        except Exception as e:
            logger.error(f"Error loading chunks: {str(e)}")
            
        return [] 