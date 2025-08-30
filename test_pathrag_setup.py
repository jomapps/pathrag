#!/usr/bin/env python3
"""
Test script to verify PathRAG with ArangoDB setup
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Test basic imports first
    print("Testing basic imports...")
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
    
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Environment variables loaded from {env_path}")
    else:
        print("✗ .env file not found")
    
    # Test ArangoDB connection directly
    print("\nTesting ArangoDB connection...")
    from arango import ArangoClient
    
    # Get ArangoDB configuration from environment
    arangodb_host = os.getenv('ARANGODB_HOST', 'localhost')
    arangodb_port = int(os.getenv('ARANGODB_PORT', '8529'))
    arangodb_username = os.getenv('ARANGODB_USERNAME', 'root')
    arangodb_password = os.getenv('ARANGODB_PASSWORD', '')
    arangodb_database = os.getenv('ARANGODB_DATABASE', 'pathrag')
    
    print(f"  - Host: {arangodb_host}:{arangodb_port}")
    print(f"  - Database: {arangodb_database}")
    print(f"  - Username: {arangodb_username}")
    
    # Test connection
    client = ArangoClient(hosts=f'http://{arangodb_host}:{arangodb_port}')
    sys_db = client.db('_system', username=arangodb_username, password=arangodb_password)
    
    # Test if we can connect
    version = sys_db.version()
    print(f"✓ ArangoDB connection successful - Version: {version}")
    
    # Test if database exists or create it
    if sys_db.has_database(arangodb_database):
        print(f"✓ Database '{arangodb_database}' exists")
    else:
        print(f"! Database '{arangodb_database}' does not exist, creating...")
        sys_db.create_database(arangodb_database)
        print(f"✓ Database '{arangodb_database}' created")
    
    # Test database access
    db = client.db(arangodb_database, username=arangodb_username, password=arangodb_password)
    collections = db.collections()
    print(f"✓ Database access successful - Collections: {len(collections)}")
    
    # Test OpenAI configuration
    print("\nTesting OpenAI configuration...")
    openai_api_key = os.getenv('OPENAI_API_KEY', '')
    if openai_api_key and openai_api_key.startswith('sk-'):
        print("✓ OpenAI API key configured")
    else:
        print("✗ OpenAI API key not configured or invalid")
    
    # Test our custom ArangoDB storage
    print("\nTesting custom ArangoDB storage...")
    from arangodb_storage import create_arangodb_storage
    
    storage = create_arangodb_storage(
        namespace="test",
        host=arangodb_host,
        port=arangodb_port,
        username=arangodb_username,
        password=arangodb_password,
        database=arangodb_database,
        embedding_func=None
    )
    print("✓ ArangoDBGraphStorage created successfully")
    
    # Test basic storage operations
    print(f"✓ Storage initialized with namespace 'test'")
    print(f"  - Nodes collection: {storage.nodes_collection_name}")
    print(f"  - Edges collection: {storage.edges_collection_name}")
    print(f"  - Graph name: {storage.graph_name}")
    
    # Test storage statistics
    stats = storage.get_stats()
    print(f"✓ Storage statistics: {stats['nodes']} nodes, {stats['edges']} edges")
    
    storage.close()
    print("✓ Storage connection closed")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all dependencies are installed")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")