#!/usr/bin/env python3
"""
PathRAG Configuration Management

This module handles loading and managing configuration from environment variables
for the PathRAG application with ArangoDB integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print("No .env file found, using system environment variables")
except ImportError:
    print("python-dotenv not installed, using system environment variables only")


@dataclass
class ArangoDBConfig:
    """ArangoDB configuration settings"""
    host: str = field(default_factory=lambda: os.getenv('ARANGODB_HOST', 'localhost'))
    port: int = field(default_factory=lambda: int(os.getenv('ARANGODB_PORT', '8529')))
    username: str = field(default_factory=lambda: os.getenv('ARANGODB_USERNAME', 'root'))
    password: str = field(default_factory=lambda: os.getenv('ARANGODB_PASSWORD', ''))
    database: str = field(default_factory=lambda: os.getenv('ARANGODB_DATABASE', 'pathrag'))
    timeout: int = field(default_factory=lambda: int(os.getenv('ARANGODB_TIMEOUT', '30')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('ARANGODB_MAX_RETRIES', '3')))
    
    @property
    def connection_url(self) -> str:
        """Get the ArangoDB connection URL"""
        return f"http://{self.host}:{self.port}"
    
    def validate(self) -> bool:
        """Validate the ArangoDB configuration"""
        if not self.password:
            raise ValueError("ArangoDB password is required")
        if not self.host:
            raise ValueError("ArangoDB host is required")
        return True


@dataclass
class OpenAIConfig:
    """OpenAI configuration settings"""
    api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    api_base: str = field(default_factory=lambda: os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'))
    model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
    max_tokens: int = field(default_factory=lambda: int(os.getenv('OPENAI_MAX_TOKENS', '4000')))
    temperature: float = field(default_factory=lambda: float(os.getenv('OPENAI_TEMPERATURE', '0.1')))
    
    def validate(self) -> bool:
        """Validate the OpenAI configuration"""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
        return True


@dataclass
class PathRAGConfig:
    """PathRAG core configuration settings"""
    working_dir: str = field(default_factory=lambda: os.getenv('PATHRAG_WORKING_DIR', './pathrag_data'))
    namespace: str = field(default_factory=lambda: os.getenv('PATHRAG_NAMESPACE', 'default'))
    log_level: str = field(default_factory=lambda: os.getenv('PATHRAG_LOG_LEVEL', 'INFO'))
    
    # Processing settings
    chunk_token_size: int = field(default_factory=lambda: int(os.getenv('PATHRAG_CHUNK_TOKEN_SIZE', '1200')))
    chunk_overlap_token_size: int = field(default_factory=lambda: int(os.getenv('PATHRAG_CHUNK_OVERLAP_TOKEN_SIZE', '100')))
    entity_extract_max_gleaning: int = field(default_factory=lambda: int(os.getenv('PATHRAG_ENTITY_EXTRACT_MAX_GLEANING', '1')))
    entity_summary_to_max_tokens: int = field(default_factory=lambda: int(os.getenv('PATHRAG_ENTITY_SUMMARY_TO_MAX_TOKENS', '500')))
    embedding_batch_num: int = field(default_factory=lambda: int(os.getenv('PATHRAG_EMBEDDING_BATCH_NUM', '32')))
    embedding_func_max_async: int = field(default_factory=lambda: int(os.getenv('PATHRAG_EMBEDDING_FUNC_MAX_ASYNC', '16')))
    llm_model_max_async: int = field(default_factory=lambda: int(os.getenv('PATHRAG_LLM_MODEL_MAX_ASYNC', '16')))
    
    # Query settings
    default_top_k: int = field(default_factory=lambda: int(os.getenv('PATHRAG_DEFAULT_TOP_K', '40')))
    max_token_for_text_unit: int = field(default_factory=lambda: int(os.getenv('PATHRAG_MAX_TOKEN_FOR_TEXT_UNIT', '4000')))
    max_token_for_global_context: int = field(default_factory=lambda: int(os.getenv('PATHRAG_MAX_TOKEN_FOR_GLOBAL_CONTEXT', '3000')))
    max_token_for_local_context: int = field(default_factory=lambda: int(os.getenv('PATHRAG_MAX_TOKEN_FOR_LOCAL_CONTEXT', '5000')))
    
    # Cache settings
    enable_llm_cache: bool = field(default_factory=lambda: os.getenv('PATHRAG_ENABLE_LLM_CACHE', 'true').lower() == 'true')
    enable_embedding_cache: bool = field(default_factory=lambda: os.getenv('PATHRAG_ENABLE_EMBEDDING_CACHE', 'true').lower() == 'true')
    
    def validate(self) -> bool:
        """Validate the PathRAG configuration"""
        # Create working directory if it doesn't exist
        Path(self.working_dir).mkdir(parents=True, exist_ok=True)
        return True


@dataclass
class APIConfig:
    """API server configuration settings"""
    host: str = field(default_factory=lambda: os.getenv('FLASK_HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('FLASK_PORT', '5000')))
    debug: bool = field(default_factory=lambda: os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
    secret_key: str = field(default_factory=lambda: os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'))
    
    # Rate limiting
    rate_limit: int = field(default_factory=lambda: int(os.getenv('API_RATE_LIMIT', '100')))
    rate_limit_period: int = field(default_factory=lambda: int(os.getenv('API_RATE_LIMIT_PERIOD', '3600')))
    
    # CORS settings
    enable_cors: bool = field(default_factory=lambda: os.getenv('API_ENABLE_CORS', 'true').lower() == 'true')
    cors_origins: str = field(default_factory=lambda: os.getenv('API_CORS_ORIGINS', '*'))
    
    def validate(self) -> bool:
        """Validate the API configuration"""
        if self.port < 1 or self.port > 65535:
            raise ValueError("Invalid port number")
        return True


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    format: str = field(default_factory=lambda: os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file: str = field(default_factory=lambda: os.getenv('LOG_FILE', './logs/pathrag.log'))
    max_size: str = field(default_factory=lambda: os.getenv('LOG_MAX_SIZE', '10MB'))
    backup_count: int = field(default_factory=lambda: int(os.getenv('LOG_BACKUP_COUNT', '5')))
    
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path(self.file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.level.upper()),
            format=self.format,
            handlers=[
                logging.FileHandler(self.file),
                logging.StreamHandler()
            ]
        )


@dataclass
class Config:
    """Main configuration class that combines all configuration sections"""
    arangodb: ArangoDBConfig = field(default_factory=ArangoDBConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    pathrag: PathRAGConfig = field(default_factory=PathRAGConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Setup logging first
        self.logging.setup_logging()
        
        # Validate all configurations
        self.validate_all()
    
    def validate_all(self) -> bool:
        """Validate all configuration sections"""
        try:
            self.arangodb.validate()
            self.openai.validate()
            self.pathrag.validate()
            self.api.validate()
            logging.info("All configurations validated successfully")
            return True
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'arangodb': {
                'host': self.arangodb.host,
                'port': self.arangodb.port,
                'database': self.arangodb.database,
                'timeout': self.arangodb.timeout,
                'max_retries': self.arangodb.max_retries
            },
            'openai': {
                'api_base': self.openai.api_base,
                'model': self.openai.model,
                'max_tokens': self.openai.max_tokens,
                'temperature': self.openai.temperature
            },
            'pathrag': {
                'working_dir': self.pathrag.working_dir,
                'namespace': self.pathrag.namespace,
                'chunk_token_size': self.pathrag.chunk_token_size,
                'chunk_overlap_token_size': self.pathrag.chunk_overlap_token_size,
                'default_top_k': self.pathrag.default_top_k
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'debug': self.api.debug
            }
        }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls()
    
    def get_pathrag_config(self) -> Dict[str, Any]:
        """Get PathRAG-specific configuration for initialization"""
        return {
            'working_dir': self.pathrag.working_dir,
            'namespace': self.pathrag.namespace,
            'chunk_token_size': self.pathrag.chunk_token_size,
            'chunk_overlap_token_size': self.pathrag.chunk_overlap_token_size,
            'entity_extract_max_gleaning': self.pathrag.entity_extract_max_gleaning,
            'entity_summary_to_max_tokens': self.pathrag.entity_summary_to_max_tokens,
            'embedding_batch_num': self.pathrag.embedding_batch_num,
            'embedding_func_max_async': self.pathrag.embedding_func_max_async,
            'llm_model_max_async': self.pathrag.llm_model_max_async,
            'enable_llm_cache': self.pathrag.enable_llm_cache,
            'enable_embedding_cache': self.pathrag.enable_embedding_cache
        }


# Global configuration instance
config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global config
    if config is None:
        config = Config.from_env()
    return config


def reload_config() -> Config:
    """Reload the configuration from environment variables"""
    global config
    config = Config.from_env()
    return config


if __name__ == '__main__':
    # Test configuration loading
    try:
        cfg = get_config()
        print("Configuration loaded successfully!")
        print(f"ArangoDB: {cfg.arangodb.connection_url}")
        print(f"OpenAI Model: {cfg.openai.model}")
        print(f"API Server: {cfg.api.host}:{cfg.api.port}")
        print(f"Working Directory: {cfg.pathrag.working_dir}")
    except Exception as e:
        print(f"Configuration error: {e}")