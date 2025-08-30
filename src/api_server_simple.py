#!/usr/bin/env python3
"""
PathRAG API Server - Simplified Version
Flask-based REST API for PathRAG with ArangoDB storage
"""

import os
import sys
import json
import traceback
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError
from dotenv import load_dotenv

# Add src directory to path for ArangoDB storage
sys.path.insert(0, str(Path(__file__).parent))

# Import ArangoDB storage
try:
    from arangodb_storage import ArangoDBGraphStorage
    ARANGODB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ArangoDB storage not available: {e}")
    ARANGODB_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
config: Optional[Dict] = None
storage: Optional[ArangoDBGraphStorage] = None


def get_config() -> Dict:
    """Get configuration from environment variables"""
    global config
    
    if config is None:
        config = {
            'api': {
                'host': os.getenv('FLASK_HOST', '0.0.0.0'),
                'port': int(os.getenv('FLASK_PORT', 5000)),
                'debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
            },
            'arangodb': {
                'host': os.getenv('ARANGODB_HOST', 'localhost'),
                'port': int(os.getenv('ARANGODB_PORT', 8529)),
                'username': os.getenv('ARANGODB_USERNAME', 'root'),
                'password': os.getenv('ARANGODB_PASSWORD', ''),
                'database': os.getenv('ARANGODB_DATABASE', 'pathrag')
            }
        }
        
    return config


def simple_embedding_func(text: str) -> List[float]:
    """Simple hash-based embedding function for testing"""
    import hashlib
    # Create a simple hash-based embedding
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()

    # Convert hex to list of floats (normalized to 0-1 range)
    embedding = []
    for i in range(0, len(hash_hex), 2):
        val = int(hash_hex[i:i+2], 16) / 255.0
        embedding.append(val)

    # Pad or truncate to 16 dimensions
    while len(embedding) < 16:
        embedding.append(0.0)
    return embedding[:16]


def get_storage() -> Optional[ArangoDBGraphStorage]:
    """Get or create ArangoDB storage instance"""
    global storage

    if storage is None and ARANGODB_AVAILABLE:
        try:
            config = get_config()
            arangodb_config = {
                "arangodb": {
                    "host": config['arangodb']['host'],
                    "port": config['arangodb']['port'],
                    "username": config['arangodb']['username'],
                    "password": config['arangodb']['password'],
                    "database": config['arangodb']['database']
                }
            }

            storage = ArangoDBGraphStorage(
                namespace="pathrag_api",
                global_config=arangodb_config,
                embedding_func=simple_embedding_func
            )

            print("✓ ArangoDB storage initialized successfully")

        except Exception as e:
            print(f"Failed to initialize ArangoDB storage: {e}")
            storage = None

    return storage


def handle_error(error: Exception, message: str = "An error occurred") -> tuple:
    """Handle errors and return JSON response"""
    error_response = {
        "error": message,
        "details": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    # Log the error
    app.logger.error(f"{message}: {error}")
    app.logger.error(traceback.format_exc())
    
    # Return appropriate status code based on error type
    if isinstance(error, BadRequest):
        return jsonify(error_response), 400
    elif isinstance(error, FileNotFoundError):
        return jsonify(error_response), 404
    else:
        return jsonify(error_response), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test ArangoDB connection
        try:
            from arango import ArangoClient
            config = get_config()

            client = ArangoClient(hosts=f"http://{config['arangodb']['host']}:{config['arangodb']['port']}")
            db = client.db(config['arangodb']['database'],
                          username=config['arangodb']['username'],
                          password=config['arangodb']['password'])

            # Simple test query
            db.version()
            arangodb_status = 'connected'

        except ImportError:
            arangodb_status = 'python-arango not installed'
        except Exception as e:
            arangodb_status = f'disconnected: {str(e)}'

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'api': 'running',
                'arangodb': arangodb_status
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'services': {
                'api': 'running',
                'arangodb': 'error'
            }
        }), 503


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'name': 'PathRAG API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'docs': '/docs',
            'query': '/query (POST)',
            'insert': '/insert (POST)'
        }
    })


@app.route('/docs', methods=['GET'])
def docs():
    """API documentation endpoint"""
    return jsonify({
        'title': 'PathRAG API Documentation',
        'version': '1.0.0',
        'description': 'REST API for PathRAG with ArangoDB storage',
        'endpoints': [
            {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            {
                'path': '/query',
                'method': 'POST',
                'description': 'Query the knowledge graph',
                'parameters': {
                    'query': 'string - The query text',
                    'top_k': 'integer - Number of results to return (optional)'
                }
            },
            {
                'path': '/insert',
                'method': 'POST',
                'description': 'Insert documents into the knowledge graph',
                'parameters': {
                    'documents': 'array - List of documents to insert'
                }
            }
        ]
    })


@app.route('/query', methods=['POST'])
def query():
    """Query PathRAG storage for relevant information"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query_text = data['query']
        top_k = data.get('top_k', 5)

        storage_instance = get_storage()
        if not storage_instance:
            return jsonify({'error': 'Storage not available'}), 500

        # Perform search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Search for relevant nodes
            results = loop.run_until_complete(
                search_nodes(storage_instance, query_text, top_k)
            )

            # Generate answer from results
            answer = generate_answer(query_text, results)

            return jsonify({
                'query': query_text,
                'answer': answer,
                'relevant_chunks': [
                    {
                        'content': r['content'],
                        'score': r.get('score', 0.0)
                    } for r in results
                ],
                'timestamp': datetime.now().isoformat()
            })

        finally:
            loop.close()

    except Exception as e:
        return jsonify({
            'error': 'Query failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


async def search_nodes(storage: ArangoDBGraphStorage, query: str, top_k: int) -> List[Dict]:
    """Search for nodes matching the query"""
    try:
        # Get query embedding
        query_embedding = simple_embedding_func(query)

        # Simple text-based search (since we don't have vector search)
        # Get all nodes and score them based on text similarity
        all_nodes = []

        # Query all text chunks
        aql_query = f"""
        FOR doc IN {storage.nodes_collection_name}
        FILTER doc.entity_type == 'text_chunk'
        RETURN doc
        """

        cursor = storage.db.aql.execute(aql_query)
        for node in cursor:
            # Simple text matching score
            content = node.get('content', '').lower()
            query_lower = query.lower()

            # Calculate simple relevance score
            score = 0.0
            query_words = query_lower.split()

            for word in query_words:
                if word in content:
                    score += 1.0

            # Normalize by query length
            if query_words:
                score = score / len(query_words)

            if score > 0:
                all_nodes.append({
                    'content': node.get('content', ''),
                    'score': score,
                    'node_id': node.get('_key', '')
                })

        # Sort by score and return top_k
        all_nodes.sort(key=lambda x: x['score'], reverse=True)
        return all_nodes[:top_k]

    except Exception as e:
        print(f"Search error: {e}")
        return []


def generate_answer(query: str, results: List[Dict]) -> str:
    """Generate an answer based on search results"""
    if not results:
        return "I don't have enough information to answer that question."

    # Simple answer generation - concatenate relevant chunks
    relevant_content = []
    for result in results[:3]:  # Use top 3 results
        if result['score'] > 0.3:  # Only use high-scoring results
            relevant_content.append(result['content'])

    if not relevant_content:
        return "I found some information but it doesn't seem directly relevant to your question."

    # Create a simple answer
    answer = "Based on the text: " + " ".join(relevant_content)

    # Truncate if too long
    if len(answer) > 500:
        answer = answer[:497] + "..."

    return answer


@app.route('/insert', methods=['POST'])
def insert():
    """Insert documents into PathRAG storage"""
    try:
        data = request.get_json()

        # Support both 'documents' (array) and 'text' (single document) formats
        if 'documents' in data:
            documents = data['documents']
        elif 'text' in data:
            documents = [data['text']]
        else:
            return jsonify({'error': 'Missing documents or text parameter'}), 400

        storage_instance = get_storage()
        if not storage_instance:
            return jsonify({'error': 'Storage not available'}), 500

        # Process documents
        inserted_count = 0
        errors = []

        for i, doc in enumerate(documents):
            try:
                # Create chunks from document (simple sentence splitting)
                chunks = split_into_chunks(doc)

                for j, chunk in enumerate(chunks):
                    if chunk.strip():  # Skip empty chunks
                        node_id = f"doc_{i}_chunk_{j}_{hash(chunk) % 10000}"

                        # Create node data
                        node_data = {
                            "content": chunk,
                            "document_index": i,
                            "chunk_index": j,
                            "entity_type": "text_chunk",
                            "embedding": simple_embedding_func(chunk)
                        }

                        # Insert node (synchronous call)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(
                                storage_instance.upsert_node(node_id, node_data)
                            )
                            if result.get('success', False):
                                inserted_count += 1
                            else:
                                errors.append(f"Failed to insert chunk {j} of document {i}")
                        finally:
                            loop.close()

            except Exception as e:
                errors.append(f"Error processing document {i}: {str(e)}")

        return jsonify({
            'message': f'Successfully inserted {inserted_count} chunks',
            'documents_processed': len(documents),
            'chunks_inserted': inserted_count,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': 'Insert failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def split_into_chunks(text: str, max_length: int = 500) -> List[str]:
    """Split text into chunks by sentences, respecting max_length"""
    import re

    # Split by sentences
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If adding this sentence would exceed max_length, start a new chunk
        if current_chunk and len(current_chunk + " " + sentence) > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


if __name__ == '__main__':
    try:
        # Load configuration
        config = get_config()
        
        # Configure Flask app
        app.config['DEBUG'] = config['api']['debug']
        
        # Set up logging
        if not app.config['DEBUG']:
            import logging
            from logging.handlers import RotatingFileHandler
            
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/pathrag_api.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('PathRAG API startup')
        
        print(f"Starting PathRAG API server...")
        print(f"Host: {config['api']['host']}")
        print(f"Port: {config['api']['port']}")
        print(f"Debug: {config['api']['debug']}")
        print(f"ArangoDB: {config['arangodb']['host']}:{config['arangodb']['port']}")
        
        # Run the Flask app
        app.run(
            host=config['api']['host'],
            port=config['api']['port'],
            debug=config['api']['debug'],
            threaded=True
        )
        
    except Exception as e:
        print(f"Failed to start PathRAG API server: {e}")
        traceback.print_exc()
        sys.exit(1)
