#!/usr/bin/env python3
"""
PathRAG with ArangoDB Setup
One-click deployment solution for PathRAG with ArangoDB storage
"""

import os
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Version
VERSION = "1.0.0"

setup(
    name="pathrag-arangodb",
    version=VERSION,
    author="PathRAG ArangoDB Team",
    author_email="contact@pathrag-arangodb.com",
    description="One-click deployment solution for PathRAG with ArangoDB storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pathrag/pathrag-arangodb",
    project_urls={
        "Bug Tracker": "https://github.com/pathrag/pathrag-arangodb/issues",
        "Documentation": "https://github.com/pathrag/pathrag-arangodb/docs",
        "Source Code": "https://github.com/pathrag/pathrag-arangodb",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "optional-dbs": [
            "neo4j>=5.0.0",
            "oracledb>=1.0.0",
            "psycopg[binary,pool]>=3.0.0",
            "pymilvus>=2.0.0",
            "pymongo>=4.0.0",
            "pymysql>=1.0.0",
            "sqlalchemy>=2.0.0",
        ],
        "visualization": [
            "pyvis>=0.3.0",
        ],
        "llm-extras": [
            "ollama>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pathrag-server=src.api_server:main",
            "pathrag-deploy=deploy.deploy:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json", "*.env"],
    },
    zip_safe=False,
    keywords=[
        "pathrag",
        "arangodb",
        "knowledge-graph",
        "rag",
        "retrieval-augmented-generation",
        "graph-database",
        "ai",
        "machine-learning",
        "nlp",
        "vector-database",
    ],
)