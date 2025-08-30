#!/usr/bin/env python3
"""
PathRAG Configuration Package

This package provides configuration management and factory functions
for PathRAG with ArangoDB integration.
"""

from .config import (
    Config,
    ArangoDBConfig,
    OpenAIConfig,
    PathRAGConfig,
    APIConfig,
    LoggingConfig,
    get_config,
    reload_config
)

from .pathrag_factory import (
    PathRAGFactory,
    create_pathrag_with_arangodb,
    test_pathrag_setup,
    get_pathrag_health
)

__version__ = "1.0.0"
__author__ = "PathRAG Team"
__description__ = "Configuration management for PathRAG with ArangoDB"

__all__ = [
    # Configuration classes
    "Config",
    "ArangoDBConfig",
    "OpenAIConfig",
    "PathRAGConfig",
    "APIConfig",
    "LoggingConfig",
    
    # Configuration functions
    "get_config",
    "reload_config",
    
    # Factory classes and functions
    "PathRAGFactory",
    "create_pathrag_with_arangodb",
    "test_pathrag_setup",
    "get_pathrag_health"
]