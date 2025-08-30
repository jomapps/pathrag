#!/usr/bin/env python3
"""
PathRAG Factory Module

This module provides factory functions to create and configure PathRAG instances
with ArangoDB storage using the configuration management system.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Import PathRAG components
try:
    from PathRAG.PathRAG import PathRAG
    from PathRAG.PathRAG.storage import JsonKVStorage, NanoVectorDBStorage
    from PathRAG.PathRAG.llm import gpt_4o_mini_complete, openai_embedding
except ImportError as e:
    logging.error(f"Failed to import PathRAG components: {e}")
    raise

# Import our custom components
try:
    from arangodb_storage import ArangoDBGraphStorage
    from config import get_config, Config
except ImportError as e:
    logging.error(f"Failed to import custom components: {e}")
    raise

logger = logging.getLogger(__name__)


class PathRAGFactory:
    """Factory class for creating PathRAG instances with different configurations"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the factory with configuration"""
        self.config = config or get_config()
        self.embedding_func = openai_embedding
        logger.info("PathRAG Factory initialized")
    
    def create_arangodb_storage(self) -> ArangoDBGraphStorage:
        """Create and configure ArangoDB graph storage"""
        try:
            arangodb_config = {
                "host": self.config.arangodb.host,
                "port": self.config.arangodb.port,
                "username": self.config.arangodb.username,
                "password": self.config.arangodb.password,
                "database": self.config.arangodb.database,
                "timeout": self.config.arangodb.timeout
            }
            
            storage = ArangoDBGraphStorage(
                namespace=self.config.pathrag.namespace,
                global_config={"arangodb": arangodb_config},
                embedding_func=openai_embedding
            )
            logger.info(f"ArangoDB storage created: {self.config.arangodb.connection_url}")
            return storage
        except Exception as e:
            logger.error(f"Failed to create ArangoDB storage: {e}")
            raise
    
    def create_kv_storage(self) -> JsonKVStorage:
        """Create and configure key-value storage"""
        try:
            working_dir = Path(self.config.pathrag.working_dir)
            working_dir.mkdir(parents=True, exist_ok=True)
            
            kv_storage = JsonKVStorage(
                namespace=self.config.pathrag.namespace,
                global_config={
                    "working_dir": str(working_dir)
                },
                embedding_func=self.embedding_func
            )
            logger.info(f"KV storage created in: {working_dir}")
            return kv_storage
        except Exception as e:
            logger.error(f"Failed to create KV storage: {e}")
            raise
    
    def create_vector_storage(self) -> NanoVectorDBStorage:
        """Create and configure vector storage"""
        try:
            working_dir = Path(self.config.pathrag.working_dir)
            working_dir.mkdir(parents=True, exist_ok=True)
            
            vector_storage = NanoVectorDBStorage(
                namespace=self.config.pathrag.namespace,
                global_config={
                    "working_dir": str(working_dir),
                    "embedding_batch_num": self.config.pathrag.embedding_batch_num,
                    "embedding_func_max_async": self.config.pathrag.embedding_func_max_async
                },
                embedding_func=self.embedding_func
            )
            logger.info(f"Vector storage created in: {working_dir}")
            return vector_storage
        except Exception as e:
            logger.error(f"Failed to create vector storage: {e}")
            raise
    
    def create_llm_config(self) -> Dict[str, Any]:
        """Create LLM configuration"""
        return {
            "llm_model_func": gpt_4o_mini_complete,
            "llm_model_name": self.config.openai.model,
            "llm_model_max_async": self.config.pathrag.llm_model_max_async,
            "llm_model_kwargs": {
                "api_key": self.config.openai.api_key,
                "base_url": self.config.openai.api_base,
                "max_tokens": self.config.openai.max_tokens,
                "temperature": self.config.openai.temperature
            }
        }
    
    def create_pathrag_instance(self) -> PathRAG:
        """Create a complete PathRAG instance with ArangoDB"""
        try:
            logger.info("Creating PathRAG instance with ArangoDB...")
            
            # Create LLM configuration
            llm_config = self.create_llm_config()
            
            # Create custom PathRAG class with ArangoDB support
            class CustomPathRAG(PathRAG):
                def _get_storage_class(self):
                    storage_classes = super()._get_storage_class()
                    storage_classes["ArangoDBGraphStorage"] = ArangoDBGraphStorage
                    return storage_classes
            
            # Create PathRAG configuration with ArangoDB settings
            pathrag_config = {
                "working_dir": self.config.pathrag.working_dir,
                "graph_storage": "ArangoDBGraphStorage",  # Use string name
                "chunk_token_size": self.config.pathrag.chunk_token_size,
                "chunk_overlap_token_size": self.config.pathrag.chunk_overlap_token_size,
                "entity_extract_max_gleaning": self.config.pathrag.entity_extract_max_gleaning,
                "entity_summary_to_max_tokens": self.config.pathrag.entity_summary_to_max_tokens,
                "enable_llm_cache": self.config.pathrag.enable_llm_cache,
                "embedding_batch_num": self.config.pathrag.embedding_batch_num,
                "embedding_func_max_async": self.config.pathrag.embedding_func_max_async,
                # Add ArangoDB configuration through addon_params
                "addon_params": {
                    "arangodb": {
                        "host": self.config.arangodb.host,
                        "port": self.config.arangodb.port,
                        "username": self.config.arangodb.username,
                        "password": self.config.arangodb.password,
                        "database": self.config.arangodb.database,
                        "timeout": self.config.arangodb.timeout
                    }
                },
                **llm_config
            }
            
            # Create PathRAG instance
            pathrag = CustomPathRAG(**pathrag_config)
            
            logger.info("PathRAG instance created successfully")
            return pathrag
            
        except Exception as e:
            logger.error(f"Failed to create PathRAG instance: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test all connections (ArangoDB, OpenAI)"""
        try:
            logger.info("Testing connections...")
            
            # Test ArangoDB connection
            arangodb_storage = self.create_arangodb_storage()
            arangodb_storage.close()
            logger.info("ArangoDB connection test passed")
            
            # Test OpenAI connection (basic validation)
            if not self.config.openai.api_key or not self.config.openai.api_key.startswith('sk-'):
                raise ValueError("Invalid OpenAI API key")
            logger.info("OpenAI configuration test passed")
            
            logger.info("All connection tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all components"""
        status = {
            "timestamp": None,
            "overall_status": "unknown",
            "components": {
                "arangodb": {"status": "unknown", "details": ""},
                "openai": {"status": "unknown", "details": ""},
                "pathrag": {"status": "unknown", "details": ""}
            }
        }
        
        try:
            from datetime import datetime
            status["timestamp"] = datetime.utcnow().isoformat()
            
            # Check ArangoDB
            try:
                arangodb_storage = self.create_arangodb_storage()
                arangodb_storage.close()
                status["components"]["arangodb"] = {
                    "status": "healthy",
                    "details": f"Connected to {self.config.arangodb.connection_url}"
                }
            except Exception as e:
                status["components"]["arangodb"] = {
                    "status": "unhealthy",
                    "details": str(e)
                }
            
            # Check OpenAI configuration
            try:
                self.config.openai.validate()
                status["components"]["openai"] = {
                    "status": "healthy",
                    "details": f"Model: {self.config.openai.model}"
                }
            except Exception as e:
                status["components"]["openai"] = {
                    "status": "unhealthy",
                    "details": str(e)
                }
            
            # Check PathRAG working directory
            try:
                working_dir = Path(self.config.pathrag.working_dir)
                working_dir.mkdir(parents=True, exist_ok=True)
                status["components"]["pathrag"] = {
                    "status": "healthy",
                    "details": f"Working dir: {working_dir}"
                }
            except Exception as e:
                status["components"]["pathrag"] = {
                    "status": "unhealthy",
                    "details": str(e)
                }
            
            # Determine overall status
            all_healthy = all(
                comp["status"] == "healthy" 
                for comp in status["components"].values()
            )
            status["overall_status"] = "healthy" if all_healthy else "unhealthy"
            
        except Exception as e:
            status["overall_status"] = "error"
            status["error"] = str(e)
        
        return status


# Convenience functions
def create_pathrag_instance(config: Optional[Config] = None) -> PathRAG:
    """Create PathRAG instance with ArangoDB"""
    factory = PathRAGFactory(config)
    return factory.create_pathrag_instance()

def create_pathrag_with_arangodb(config: Optional[Config] = None) -> PathRAG:
    """Convenience function to create PathRAG with ArangoDB"""
    factory = PathRAGFactory(config)
    return factory.create_pathrag_instance()


def test_pathrag_setup(config: Optional[Config] = None) -> bool:
    """Test the complete PathRAG setup"""
    factory = PathRAGFactory(config)
    return factory.test_connection()


def get_pathrag_health(config: Optional[Config] = None) -> Dict[str, Any]:
    """Get PathRAG health status"""
    factory = PathRAGFactory(config)
    return factory.get_health_status()


if __name__ == '__main__':
    # Test the factory
    try:
        print("Testing PathRAG Factory...")
        
        # Test configuration loading
        config = get_config()
        print(f"✓ Configuration loaded")
        
        # Test factory creation
        factory = PathRAGFactory(config)
        print(f"✓ Factory created")
        
        # Test connections
        if factory.test_connection():
            print(f"✓ Connection tests passed")
        else:
            print(f"✗ Connection tests failed")
        
        # Get health status
        health = factory.get_health_status()
        print(f"Health Status: {health['overall_status']}")
        for component, status in health['components'].items():
            print(f"  {component}: {status['status']} - {status['details']}")
        
        # Try creating PathRAG instance
        print("\nCreating PathRAG instance...")
        pathrag = factory.create_pathrag_instance()
        print(f"✓ PathRAG instance created successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()