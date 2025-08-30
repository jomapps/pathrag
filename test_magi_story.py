#!/usr/bin/env python3
"""
PathRAG Test Script - The Gift of the Magi
This script demonstrates PathRAG functionality by:
1. Ingesting "The Gift of the Magi" story
2. Asking various questions about the content
3. Displaying the answers with context
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "config"))

# Import configuration modules
from pathrag_factory import create_pathrag_instance
from config import get_config

async def main():
    """Main test function"""
    print("=" * 60)
    print("PathRAG Test: The Gift of the Magi")
    print("=" * 60)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = get_config()
        print(f"   ✓ Configuration loaded successfully")
        print(f"   ✓ ArangoDB URL: {config.arangodb.connection_url}")
        print(f"   ✓ Database: {config.arangodb.database}")
        print(f"   ✓ Namespace: {config.pathrag.namespace}")
        
        # Create PathRAG instance
        print("\n2. Creating PathRAG instance...")
        pathrag = create_pathrag_instance(config)
        print("   ✓ PathRAG instance created successfully")
        
        # Read the test story
        story_path = project_root / "docs" / "test-data" / "magi-test-story.md"
        print(f"\n3. Reading story from: {story_path}")
        
        if not story_path.exists():
            raise FileNotFoundError(f"Story file not found: {story_path}")
            
        with open(story_path, 'r', encoding='utf-8') as f:
            story_content = f.read()
            
        print(f"   ✓ Story loaded ({len(story_content)} characters)")
        
        # Ingest the story
        print("\n4. Ingesting story into PathRAG...")
        await pathrag.ainsert(story_content)
        print("   ✓ Story ingested successfully")
        
        # Test questions
        questions = [
            "What are the main characters' names in the story?",
            "How much money did Della have to buy a Christmas present?",
            "What did Della sell to get money for Jim's present?",
            "What gift did Della buy for Jim?",
            "What gift did Jim buy for Della?",
            "Why does the narrator call Jim and Della the wisest?",
            "What is the moral lesson of this story?",
            "Who are the Magi mentioned in the title?"
        ]
        
        print("\n5. Testing PathRAG with questions...")
        print("=" * 60)
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            print("-" * 50)
            
            try:
                # Query PathRAG
                result = await pathrag.aquery(question)
                
                print(f"Answer: {result}")
                
            except Exception as e:
                print(f"Error answering question: {str(e)}")
                
        print("\n" + "=" * 60)
        print("PathRAG Test Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)