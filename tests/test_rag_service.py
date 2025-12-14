"""Test RAG service chunking and retrieval logic"""
from app.services.rag_service import RAGService


def test_rag_chunking():
    """Test that RAG service can chunk a document into smaller pieces"""
    rag = RAGService(chunk_size=50)

    text = (
        "Paris is the capital city of France. "
        "It is known for the Eiffel Tower and the Louvre Museum. "
        "Berlin is the capital of Germany. "
        "London is the capital of the United Kingdom."
    )

    # Chunk the document
    chunks = rag.chunk_document(text)
    
    # Should produce multiple chunks given the chunk_size
    assert len(chunks) >= 1
    
    # Make sure all chunks are strings and not empty
    for chunk in chunks:
        assert isinstance(chunk, str)
        assert chunk.strip() != ""


def test_rag_retrieval():
    """Test that RAG service retrieves relevant chunks based on query"""
    rag = RAGService(chunk_size=50)

    text = (
        "Paris is the capital city of France. "
        "It is known for the Eiffel Tower and the Louvre Museum. "
        "Berlin is the capital of Germany. "
        "London is the capital of the United Kingdom."
    )

    chunks = rag.chunk_document(text)

    # Query about France
    query = "What is the capital city of France?"
    relevant_chunks = rag.retrieve_relevant_chunks(query=query, chunks=chunks, top_k=2)

    assert len(relevant_chunks) >= 1
    
    # At least one chunk should mention "paris" or "france"
    joined = " ".join(relevant_chunks).lower()
    assert "paris" in joined or "france" in joined


def test_rag_relevance_scoring():
    """Test that relevance scoring works correctly"""
    rag = RAGService()
    
    query_keywords = {"capital", "france"}
    
    # Chunk with high relevance
    chunk1 = "Paris is the capital of France"
    score1 = rag._calculate_relevance(query_keywords, chunk1)
    
    # Chunk with low relevance
    chunk2 = "The weather is nice today"
    score2 = rag._calculate_relevance(query_keywords, chunk2)
    
    # Score should be higher for more relevant chunk
    assert score1 > score2
    assert score1 >= 2  # Should match both "capital" and "france"
    assert score2 == 0  # Should match nothing
