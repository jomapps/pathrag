#!/usr/bin/env python3
"""
PathRAG API Server
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

# Add PathRAG to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PathRAG'))

from PathRAG.PathRAG import PathRAG
from PathRAG.base import QueryParam
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_config, PathRAGConfig
from config.pathrag_factory import PathRAGFactory

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
pathrag_instance: Optional[PathRAG] = None
config: Optional[PathRAGConfig] = None


def get_pathrag_instance() -> PathRAG:
    """Get or create PathRAG instance"""
    global pathrag_instance, config
    
    if pathrag_instance is None:
        config = get_config()
        factory = PathRAGFactory(config)
        pathrag_instance = factory.create_pathrag()
        
    return pathrag_instance


def handle_error(error: Exception, message: str = "An error occurred") -> tuple:
    """Handle errors consistently"""
    error_details = {
        'error': str(error),
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'type': type(error).__name__
    }
    
    if config and config.api.debug:
        error_details['traceback'] = traceback.format_exc()
    
    app.logger.error(f"{message}: {error}")
    
    if isinstance(error, BadRequest):
        return jsonify(error_details), 400
    elif isinstance(error, FileNotFoundError):
        return jsonify(error_details), 404
    else:
        return jsonify(error_details), 500


@app.before_request
def before_request():
    """Log incoming requests"""
    g.start_time = datetime.now()
    app.logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")


@app.after_request
def after_request(response):
    """Log response details"""
    if hasattr(g, 'start_time'):
        duration = (datetime.now() - g.start_time).total_seconds()
        app.logger.info(f"Response: {response.status_code} in {duration:.3f}s")
    return response


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        config = get_config()
        factory = PathRAGFactory(config)
        
        # Test connections
        arangodb_status = factory.test_arangodb_connection()
        
        health_status = {
            'status': 'healthy' if arangodb_status else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'components': {
                'arangodb': 'connected' if arangodb_status else 'disconnected',
                'pathrag': 'ready' if pathrag_instance else 'not_initialized'
            }
        }
        
        status_code = 200 if arangodb_status else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        return handle_error(e, "Health check failed")


@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed system status"""
    try:
        config = get_config()
        factory = PathRAGFactory(config)
        
        status = factory.get_health_status()
        return jsonify(status)
        
    except Exception as e:
        return handle_error(e, "Failed to get system status")


@app.route('/insert', methods=['POST'])
def insert_documents():
    """Insert documents into PathRAG"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        # Extract documents from request
        documents = data.get('documents')
        if not documents:
            raise BadRequest("No 'documents' field provided")
        
        if isinstance(documents, str):
            documents = [documents]
        elif not isinstance(documents, list):
            raise BadRequest("'documents' must be a string or list of strings")
        
        # Get PathRAG instance and insert documents
        pathrag = get_pathrag_instance()
        result = pathrag.insert(documents)
        
        response = {
            'message': f'Successfully inserted {len(documents)} document(s)',
            'document_count': len(documents),
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        return handle_error(e, "Failed to insert documents")


@app.route('/insert_custom_kg', methods=['POST'])
def insert_custom_kg():
    """Insert custom knowledge graph data"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        custom_kg = data.get('custom_kg')
        if not custom_kg:
            raise BadRequest("No 'custom_kg' field provided")
        
        # Validate custom_kg structure
        required_fields = ['chunks', 'entities', 'relationships']
        for field in required_fields:
            if field not in custom_kg:
                raise BadRequest(f"Missing required field '{field}' in custom_kg")
        
        # Get PathRAG instance and insert custom KG
        pathrag = get_pathrag_instance()
        result = pathrag.insert_custom_kg(custom_kg)
        
        response = {
            'message': 'Successfully inserted custom knowledge graph',
            'chunks_count': len(custom_kg.get('chunks', [])),
            'entities_count': len(custom_kg.get('entities', [])),
            'relationships_count': len(custom_kg.get('relationships', [])),
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        return handle_error(e, "Failed to insert custom knowledge graph")


@app.route('/query', methods=['POST'])
def query_pathrag():
    """Query PathRAG knowledge base"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        query_text = data.get('query')
        if not query_text:
            raise BadRequest("No 'query' field provided")
        
        # Parse query parameters
        query_params = data.get('params', {})
        
        # Create QueryParam object
        param = QueryParam(
            mode=query_params.get('mode', 'hybrid'),
            only_need_context=query_params.get('only_need_context', False),
            response_type=query_params.get('response_type', 'Multiple Paragraphs'),
            top_k=query_params.get('top_k', 60),
            max_token_for_text_unit=query_params.get('max_token_for_text_unit', 4000),
            max_token_for_global_context=query_params.get('max_token_for_global_context', 4000),
            max_token_for_local_context=query_params.get('max_token_for_local_context', 4000)
        )
        
        # Get PathRAG instance and perform query
        pathrag = get_pathrag_instance()
        result = pathrag.query(query_text, param)
        
        response = {
            'query': query_text,
            'result': result,
            'params': query_params,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return handle_error(e, "Failed to query PathRAG")


@app.route('/delete_entity', methods=['DELETE'])
def delete_entity():
    """Delete an entity and its relationships"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        entity_name = data.get('entity_name')
        if not entity_name:
            raise BadRequest("No 'entity_name' field provided")
        
        # Get PathRAG instance and delete entity
        pathrag = get_pathrag_instance()
        result = pathrag.delete_by_entity(entity_name)
        
        response = {
            'message': f'Successfully deleted entity: {entity_name}',
            'entity_name': entity_name,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return handle_error(e, "Failed to delete entity")


@app.route('/config', methods=['GET'])
def get_config_info():
    """Get current configuration (sanitized)"""
    try:
        config = get_config()
        
        # Sanitize sensitive information
        config_dict = {
            'arangodb': {
                'host': config.arangodb.host,
                'port': config.arangodb.port,
                'database': config.arangodb.database,
                'connected': True  # We'll test this
            },
            'pathrag': {
                'working_dir': config.pathrag.working_dir,
                'chunk_token_size': config.pathrag.chunk_token_size,
                'embedding_batch_num': config.pathrag.embedding_batch_num,
                'llm_model_name': config.pathrag.llm_model_name
            },
            'api_server': {
            'host': config.api.host,
            'port': config.api.port,
            'debug': config.api.debug
        }
        }
        
        return jsonify(config_dict), 200
        
    except Exception as e:
        return handle_error(e, "Failed to get configuration")


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get PathRAG statistics"""
    try:
        pathrag = get_pathrag_instance()
        
        # Get basic statistics (this would need to be implemented in PathRAG)
        stats = {
            'timestamp': datetime.now().isoformat(),
            'status': 'active',
            'message': 'PathRAG instance is running'
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return handle_error(e, "Failed to get statistics")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """Application factory"""
    if config_override:
        # Apply configuration overrides
        for key, value in config_override.items():
            app.config[key] = value
    
    return app


if __name__ == '__main__':
    try:
        # Load configuration
        config = get_config()
        
        # Configure Flask app
        app.config['DEBUG'] = config.api.debug
        
        # Set up logging
        if not app.debug:
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
        print(f"Host: {config.api.host}")
        print(f"Port: {config.api.port}")
        print(f"Debug: {config.api.debug}")
        print(f"ArangoDB: {config.arangodb.host}:{config.arangodb.port}")
        
        # Run the Flask app
        app.run(
            host=config.api.host,
            port=config.api.port,
            debug=config.api.debug,
            threaded=True
        )
        
    except Exception as e:
        print(f"Failed to start PathRAG API server: {e}")
        traceback.print_exc()
        sys.exit(1)