#!/usr/bin/env python3
"""
PathRAG API Server - Simplified Version
Flask-based REST API for PathRAG with ArangoDB storage
"""

import os
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
config: Optional[Dict] = None


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
    """Query endpoint - placeholder for now"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
            
        query_text = data['query']
        top_k = data.get('top_k', 10)
        
        # Placeholder response
        return jsonify({
            'query': query_text,
            'results': [],
            'message': 'PathRAG functionality not yet implemented - this is a placeholder response',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Query failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/insert', methods=['POST'])
def insert():
    """Insert endpoint - placeholder for now"""
    try:
        data = request.get_json()
        if not data or 'documents' not in data:
            return jsonify({'error': 'Missing documents parameter'}), 400
            
        documents = data['documents']
        
        # Placeholder response
        return jsonify({
            'message': 'PathRAG functionality not yet implemented - this is a placeholder response',
            'documents_received': len(documents),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Insert failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


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
