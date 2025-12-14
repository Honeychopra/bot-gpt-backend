"""RAG Service for document-based Q&A"""
from typing import List
import re

class RAGService:
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            
            if current_length >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def retrieve_relevant_chunks(
        self, 
        query: str, 
        chunks: List[str], 
        top_k: int = 3
    ) -> List[str]:
        """Find most relevant chunks using keyword matching"""
        query_keywords = set(query.lower().split())
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_relevance(query_keywords, chunk)
            scored_chunks.append((score, chunk))
        
        # Sort by score and return top K
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def _calculate_relevance(self, query_keywords: set, chunk: str) -> int:
        """Calculate relevance score (simple word overlap)"""
        chunk_words = set(chunk.lower().split())
        overlap = query_keywords.intersection(chunk_words)
        return len(overlap)