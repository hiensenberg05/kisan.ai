#!/usr/bin/env python3
"""
Test script for RAG system debugging
"""

import asyncio
import logging
from tools.rag import RAGTool

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_rag_system():
    """Test the RAG system step by step"""
    
    print("=== RAG System Test ===")
    
    try:
        # Initialize RAG tool
        print("1. Initializing RAG tool...")
        rag_tool = RAGTool()
        print("✓ RAG tool initialized successfully")
        
        # Test connection
        print("\n2. Testing RAG connection...")
        connection_ok = await rag_tool.test_connection()
        if connection_ok:
            print("✓ RAG connection successful")
        else:
            print("✗ RAG connection failed")
            return
        
        # Test corpus stats
        print("\n3. Getting corpus statistics...")
        stats = await rag_tool.get_corpus_stats()
        print(f"✓ Corpus stats: {stats}")
        
        # Test simple query
        print("\n4. Testing simple query...")
        test_query = "What are the best crops for Karnataka?"
        print(f"Query: {test_query}")
        
        response = await rag_tool.query_knowledge(test_query)
        print(f"✓ Response: {response[:200]}...")
        
        # Test disease search
        print("\n5. Testing disease search...")
        disease_response = await rag_tool.search_diseases("tomato", "yellow leaves")
        print(f"✓ Disease response: {disease_response[:200]}...")
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_rag_system()) 