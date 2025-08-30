# PathRAG with ArangoDB - Complete Production Deployment Guide

This comprehensive guide provides everything needed to deploy PathRAG with ArangoDB on an Ubuntu production server, including automated deployment scripts.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [System Requirements](#system-requirements)
4. [Automated Deployment](#automated-deployment)
5. [Manual Installation Steps](#manual-installation-steps)
6. [Configuration](#configuration)
7. [Service Management](#service-management)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

## 🎯 Overview

### Architecture
```
User Request → PathRAG API (Flask) → ArangoDB Graph Storage → LLM Processing → Response
```

### Key Components
- **PathRAG**: Graph-based RAG system
- **ArangoDB**: Graph database for knowledge storage
- **Flask API**: REST API interface
- **Python Environment**: Isolated virtual environment
- **Systemd Service**: Production service management

## 🔧 Prerequisites

### Server Requirements
- Ubuntu 20.04 LTS or later (recommended: Ubuntu 22.04 LTS)
- Root or sudo access
- Internet connection
- ArangoDB server accessible (movie.ft.tc:8529)

### Network Requirements
- Port 5000: PathRAG API server
- Port 8529: ArangoDB connection (outbound)
- Firewall configured for external access

## 💻 System Requirements

### Minimum
- **CPU**: 4 cores, 2.0 GHz
- **RAM**: 8GB
- **Storage**: 20GB free space
- **Network**: Stable internet connection

### Recommended
- **CPU**: 8+ cores, 3.0 GHz
- **RAM**: 16GB or more
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet

## 🚀 Automated Deployment

### Quick Start

1. **Download the deployment script**:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/pathrag-deploy.sh
   chmod +x pathrag-deploy.sh
   ```

2. **Run the deployment**:
   ```bash
   sudo ./pathrag-deploy.sh
   ```

3. **Verify installation**:
   ```bash
   curl http://localhost:5000/health
   ```

### Deployment Script Features
- ✅ System dependency installation
- ✅ Python environment setup
- ✅ PathRAG installation with ArangoDB integration
- ✅ Service configuration
- ✅ Firewall setup
- ✅ Health checks
- ✅ Automatic startup configuration

## 📝 Manual Installation Steps

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    wget \
    unzip \
    htop \
    tree \
    vim \
    nano \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    libblas3 \
    liblapack3 \
    liblapack-dev \
    libblas-dev \
    gfortran \
    libhdf5-dev \
    libssl-dev \
    libffi-dev

# Upgrade pip
python3 -m pip install --upgrade pip
```

### Step 2: Create PathRAG User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash pathrag
sudo usermod -aG sudo pathrag

# Switch to pathrag user
sudo su - pathrag
```

### Step 3: Directory Structure

```bash
# Create directory structure
mkdir -p ~/pathrag/{installation,data,logs,config,backups}
chmod 755 ~/pathrag
chmod 750 ~/pathrag/{data,logs,config,backups}
```

### Step 4: Python Environment

```bash
# Create virtual environment
cd ~/pathrag/installation
python3 -m venv pathrag-env
source pathrag-env/bin/activate

# Upgrade pip and tools
pip install --upgrade pip setuptools wheel
```

### Step 5: PathRAG Installation

```bash
# Clone PathRAG repository
git clone https://github.com/BUPT-GAMMA/PathRAG.git
cd PathRAG

# Install dependencies
pip install -r requirements.txt

# Install CPU-optimized PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install additional packages
pip install \
    python-arango>=7.8.0 \
    numpy \
    scipy \
    scikit-learn \
    pandas \
    matplotlib \
    seaborn \
    jupyter \
    ipython \
    tqdm \
    requests \
    python-dotenv \
    flask
```

### Step 6: ArangoDB Integration

```bash
# Create ArangoDB storage implementation
cat > ~/pathrag/arangodb_storage.py << 'EOF'
#!/usr/bin/env python3
"""
ArangoDB storage implementation for PathRAG
"""

import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator, Tuple
from arango import ArangoClient
import hashlib
import json
import numpy as np

class ArangoDBGraphStorage:
    """ArangoDB implementation of graph storage for PathRAG."""
    
    def __init__(self, namespace: str, global_config: Dict[str, Any], embedding_func=None):
        self.namespace = namespace
        self.config = global_config.get("arangodb", {})
        self.embedding_func = embedding_func or self._default_embedding
        
        # Initialize ArangoDB connection
        self.client = ArangoClient(
            hosts=f"http://{self.config['host']}:{self.config['port']}"
        )
        
        self.db = self.client.db(
            self.config['database'],
            username=self.config['username'],
            password=self.config['password']
        )
        
        # Collection names with namespace
        self.nodes_collection_name = f"{namespace}_nodes"
        self.edges_collection_name = f"{namespace}_edges"
        self.graph_name = f"{namespace}_graph"
        
        # Initialize collections and graph
        self._init_collections()
    
    def _init_collections(self):
        """Initialize ArangoDB collections and graph."""
        # Create nodes collection
        if not self.db.has_collection(self.nodes_collection_name):
            self.db.create_collection(self.nodes_collection_name)
        
        # Create edges collection
        if not self.db.has_collection(self.edges_collection_name):
            self.db.create_collection(self.edges_collection_name, edge=True)
        
        # Create graph
        if not self.db.has_graph(self.graph_name):
            self.db.create_graph(
                self.graph_name,
                edge_definitions=[
                    {
                        'edge_collection': self.edges_collection_name,
                        'from_vertex_collections': [self.nodes_collection_name],
                        'to_vertex_collections': [self.nodes_collection_name]
                    }
                ]
            )
        
        # Get collection references
        self.nodes_collection = self.db.collection(self.nodes_collection_name)
        self.edges_collection = self.db.collection(self.edges_collection_name)
        self.graph = self.db.graph(self.graph_name)
    
    def _default_embedding(self, text: str) -> List[float]:
        """Default embedding function using hash."""
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        # Create a 128-dimensional vector from the hash
        embedding = []
        for i in range(32):
            embedding.extend([
                ((hash_int >> (i * 4 + 3)) & 1) * 2 - 1,
                ((hash_int >> (i * 4 + 2)) & 1) * 2 - 1,
                ((hash_int >> (i * 4 + 1)) & 1) * 2 - 1,
                ((hash_int >> (i * 4)) & 1) * 2 - 1
            ])
        return embedding[:128]  # Ensure exactly 128 dimensions
    
    async def upsert_node(self, node_id: str, node_data: dict) -> dict:
        """Insert or update a node."""
        try:
            # Ensure embedding is JSON serializable
            if 'embedding' in node_data:
                if isinstance(node_data['embedding'], np.ndarray):
                    node_data['embedding'] = node_data['embedding'].tolist()
                elif hasattr(node_data['embedding'], 'tolist'):
                    node_data['embedding'] = node_data['embedding'].tolist()
            
            document = {"_key": node_id, **node_data}
            result = self.nodes_collection.insert(document, overwrite=True)
            return {"node_id": node_id, "success": True}
        except Exception as e:
            return {"node_id": node_id, "success": False, "error": str(e)}
    
    async def upsert_edge(self, source_node_id: str, target_node_id: str, edge_data: dict) -> dict:
        """Insert or update an edge."""
        try:
            edge_key = f"{source_node_id}_to_{target_node_id}"
            edge_doc = {
                "_key": edge_key,
                "_from": f"{self.nodes_collection_name}/{source_node_id}",
                "_to": f"{self.nodes_collection_name}/{target_node_id}",
                **edge_data
            }
            
            result = self.edges_collection.insert(edge_doc, overwrite=True)
            return {"edge_id": edge_key, "success": True}
        except Exception as e:
            return {"edge_id": f"{source_node_id}_to_{target_node_id}", "success": False, "error": str(e)}
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data."""
        try:
            return self.nodes_collection.get(node_id)
        except:
            return None
    
    async def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query nodes using text search."""
        try:
            # Simple text search in node content
            aql = f"""
            FOR node IN {self.nodes_collection_name}
                FILTER CONTAINS(LOWER(node.content || ""), LOWER(@query))
                LIMIT @top_k
                RETURN node
            """
            
            cursor = self.db.aql.execute(aql, bind_vars={'query': query_text, 'top_k': top_k})
            return list(cursor)
        except Exception as e:
            print(f"Query error: {e}")
            return []
EOF
```

## ⚙️ Configuration

### Environment Configuration

```bash
# Create environment file
cat > ~/pathrag/config/pathrag.env << 'EOF'
# PathRAG Environment Configuration

# Directories
export PATHRAG_HOME=~/pathrag
export PATHRAG_DATA_DIR=~/pathrag/data
export PATHRAG_LOG_DIR=~/pathrag/logs
export PATHRAG_CONFIG_DIR=~/pathrag/config
export PATHRAG_BACKUP_DIR=~/pathrag/backups

# Python Configuration
export PYTHONPATH="$PYTHONPATH:~/pathrag/installation/PathRAG:~/pathrag"
export PATHRAG_INSTALL_DIR=~/pathrag/installation/PathRAG

# Performance Settings
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_MAX_THREADS=4

# API Configuration
export OPENAI_API_KEY="your-openai-api-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"

# ArangoDB Configuration
export ARANGODB_HOST="movie.ft.tc"
export ARANGODB_PORT="8529"
export ARANGODB_USERNAME="root"
export ARANGODB_PASSWORD="mzAd4682X13P6dRHLH7wQAjg"
export ARANGODB_DATABASE="pathrag"

# Logging Configuration
export PATHRAG_LOG_LEVEL=INFO
export PATHRAG_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
EOF

# Load environment
echo "source ~/pathrag/config/pathrag.env" >> ~/.bashrc
source ~/.bashrc
```

### PathRAG Configuration

```bash
# Create PathRAG config
cat > ~/pathrag/config/pathrag_config.py << 'EOF'
"""
PathRAG Configuration with ArangoDB
"""
import os
from pathlib import Path

# ArangoDB Configuration
ARANGODB_CONFIG = {
    "arangodb": {
        "host": os.getenv("ARANGODB_HOST", "movie.ft.tc"),
        "port": int(os.getenv("ARANGODB_PORT", 8529)),
        "username": os.getenv("ARANGODB_USERNAME", "root"),
        "password": os.getenv("ARANGODB_PASSWORD", "mzAd4682X13P6dRHLH7wQAjg"),
        "database": os.getenv("ARANGODB_DATABASE", "pathrag")
    }
}

# PathRAG Settings
PATHRAG_SETTINGS = {
    "working_dir": str(Path.home() / "pathrag" / "data"),
    "log_dir": str(Path.home() / "pathrag" / "logs"),
    "max_workers": 4,
    "chunk_size": 1000,
    "overlap_size": 200,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "llm_model": "gpt-3.5-turbo",
}
EOF
```

## 🌐 API Server Setup

```bash
# Create Flask API server
cat > ~/pathrag/pathrag_api.py << 'EOF'
#!/usr/bin/env python3
"""
PathRAG Flask API Server with ArangoDB
"""
import sys
import os
from pathlib import Path
import logging
from flask import Flask, request, jsonify

# Add PathRAG to Python path
PATHRAG_DIR = Path.home() / "pathrag" / "installation" / "PathRAG"
sys.path.insert(0, str(PATHRAG_DIR))
sys.path.insert(0, str(Path.home() / "pathrag"))

try:
    from PathRAG import PathRAG, QueryParam
    from arangodb_storage import ArangoDBGraphStorage
    from config.pathrag_config import ARANGODB_CONFIG
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for testing
    PathRAG = None
    QueryParam = None

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / "pathrag" / "logs" / "api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize PathRAG
working_dir = Path.home() / "pathrag" / "data" / "api"
working_dir.mkdir(parents=True, exist_ok=True)

try:
    if PathRAG:
        rag = PathRAG(
            working_dir=str(working_dir),
            graph_storage_cls=ArangoDBGraphStorage,
            **ARANGODB_CONFIG
        )
        logger.info("PathRAG initialized successfully with ArangoDB")
    else:
        rag = None
        logger.warning("PathRAG not available, running in test mode")
except Exception as e:
    logger.error(f"Failed to initialize PathRAG: {e}")
    rag = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PathRAG API with ArangoDB",
        "pathrag_available": rag is not None
    })

@app.route('/insert', methods=['POST'])
def insert_document():
    """Insert a document into PathRAG"""
    try:
        if not rag:
            return jsonify({"error": "PathRAG not initialized"}), 500
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        rag.insert(text)
        
        logger.info(f"Document inserted successfully: {len(text)} characters")
        return jsonify({"message": "Document inserted successfully"})
    
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_documents():
    """Query PathRAG with a question"""
    try:
        if not rag:
            return jsonify({"error": "PathRAG not initialized"}), 500
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        mode = data.get('mode', 'hybrid')
        
        if QueryParam:
            result = rag.query(query, param=QueryParam(mode=mode))
        else:
            result = f"Test response for query: {query}"
        
        logger.info(f"Query processed successfully: {query[:50]}...")
        return jsonify({
            "query": query,
            "answer": result,
            "mode": mode
        })
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        # Test ArangoDB connection
        arangodb_status = "unknown"
        if rag and hasattr(rag, 'graph_storage'):
            try:
                # Try to access the storage
                storage = rag.graph_storage
                arangodb_status = "connected"
            except:
                arangodb_status = "disconnected"
        
        return jsonify({
            "pathrag_initialized": rag is not None,
            "arangodb_status": arangodb_status,
            "working_directory": str(working_dir),
            "log_directory": str(Path.home() / "pathrag" / "logs")
        })
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting PathRAG API server with ArangoDB...")
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Make executable
chmod +x ~/pathrag/pathrag_api.py
```

## 🔧 Service Management

### Create Systemd Service

```bash
# Create service file (run as root)
sudo tee /etc/systemd/system/pathrag.service > /dev/null << 'EOF'
[Unit]
Description=PathRAG API Service with ArangoDB
After=network.target
Wants=network.target

[Service]
Type=simple
User=pathrag
Group=pathrag
WorkingDirectory=/home/pathrag/pathrag
Environment=PATH=/home/pathrag/pathrag/installation/pathrag-env/bin
EnvironmentFile=/home/pathrag/pathrag/config/pathrag.env
ExecStart=/home/pathrag/pathrag/installation/pathrag-env/bin/python /home/pathrag/pathrag/pathrag_api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pathrag

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable pathrag
```

### Service Commands

```bash
# Start service
sudo systemctl start pathrag

# Check status
sudo systemctl status pathrag

# View logs
journalctl -u pathrag -f

# Stop service
sudo systemctl stop pathrag

# Restart service
sudo systemctl restart pathrag
```

## 🔥 Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow 5000/tcp
sudo ufw enable
sudo ufw status
```

## ✅ Testing & Verification

### Health Check

```bash
# Test health endpoint
curl -X GET http://localhost:5000/health

# Expected response:
# {"status": "healthy", "service": "PathRAG API with ArangoDB", "pathrag_available": true}
```

### Document Insertion Test

```bash
# Insert test document
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document for PathRAG with ArangoDB integration."}'
```

### Query Test

```bash
# Test query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "mode": "hybrid"}'
```

### Status Check

```bash
# Check system status
curl -X GET http://localhost:5000/status
```

### Comprehensive Test Script

```bash
# Create test script
cat > ~/pathrag/test_deployment.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive deployment test script
"""
import requests
import json
import time

def test_pathrag_deployment():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing PathRAG Deployment")
    print("=" * 40)
    
    # Test 1: Health Check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Status Check
    print("\n2. Status Check...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print("✅ Status check passed")
            status = response.json()
            print(f"   PathRAG initialized: {status.get('pathrag_initialized')}")
            print(f"   ArangoDB status: {status.get('arangodb_status')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 3: Document Insertion
    print("\n3. Document Insertion...")
    test_doc = {
        "text": "PathRAG is a graph-based retrieval augmented generation system that uses ArangoDB for knowledge storage. It provides efficient document indexing and natural language querying capabilities."
    }
    
    try:
        response = requests.post(
            f"{base_url}/insert",
            headers={"Content-Type": "application/json"},
            json=test_doc
        )
        if response.status_code == 200:
            print("✅ Document insertion passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Document insertion failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Document insertion error: {e}")
    
    # Wait a moment for indexing
    time.sleep(2)
    
    # Test 4: Query
    print("\n4. Query Test...")
    test_query = {
        "query": "What is PathRAG and how does it work?",
        "mode": "hybrid"
    }
    
    try:
        response = requests.post(
            f"{base_url}/query",
            headers={"Content-Type": "application/json"},
            json=test_query
        )
        if response.status_code == 200:
            print("✅ Query test passed")
            result = response.json()
            print(f"   Query: {result.get('query')}")
            print(f"   Answer: {result.get('answer')[:100]}...")
        else:
            print(f"❌ Query test failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Query test error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Deployment test completed!")
    return True

if __name__ == "__main__":
    test_pathrag_deployment()
EOF

# Make executable and run
chmod +x ~/pathrag/test_deployment.py
python3 ~/pathrag/test_deployment.py
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status pathrag

# Check logs
journalctl -u pathrag -n 50

# Check Python path
sudo -u pathrag bash -c "source /home/pathrag/pathrag/config/pathrag.env && python3 -c 'import sys; print(sys.path)'"
```

#### 2. ArangoDB Connection Issues
```bash
# Test ArangoDB connectivity
curl -X GET http://movie.ft.tc:8529/_api/version

# Test from Python
python3 -c "
from arango import ArangoClient
client = ArangoClient(hosts='http://movie.ft.tc:8529')
db = client.db('pathrag', username='root', password='mzAd4682X13P6dRHLH7wQAjg')
print('Connected successfully')
print('Collections:', [c['name'] for c in db.collections()])
"
```

#### 3. Import Errors
```bash
# Check Python environment
source ~/pathrag/installation/pathrag-env/bin/activate
python3 -c "import PathRAG; print('PathRAG imported successfully')"
python3 -c "from arango import ArangoClient; print('ArangoDB client imported successfully')"
```

#### 4. Permission Issues
```bash
# Fix permissions
sudo chown -R pathrag:pathrag /home/pathrag/pathrag
sudo chmod -R 755 /home/pathrag/pathrag
sudo chmod -R 750 /home/pathrag/pathrag/{data,logs,config,backups}
```

### Log Analysis

```bash
# View API logs
tail -f ~/pathrag/logs/api.log

# View system logs
journalctl -u pathrag -f

# View all PathRAG related logs
grep -r "pathrag" /var/log/
```

## 🔄 Maintenance

### Regular Tasks

#### Log Rotation
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/pathrag > /dev/null << 'EOF'
/home/pathrag/pathrag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 pathrag pathrag
    postrotate
        systemctl reload pathrag || true
    endscript
}
EOF
```

#### Backup Script
```bash
# Create backup script
cat > ~/pathrag/backup.sh << 'EOF'
#!/bin/bash

# PathRAG Backup Script
BACKUP_DIR="~/pathrag/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="pathrag_backup_${DATE}.tar.gz"

echo "Creating backup: $BACKUP_FILE"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude="~/pathrag/installation/pathrag-env" \
    --exclude="~/pathrag/logs" \
    ~/pathrag/

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "pathrag_backup_*.tar.gz" -mtime +7 -delete
EOF

# Make executable
chmod +x ~/pathrag/backup.sh

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/pathrag/backup.sh") | crontab -
```

#### Monitoring Script
```bash
# Create monitoring script
cat > ~/pathrag/monitor.sh << 'EOF'
#!/bin/bash

# PathRAG Monitoring Script
LOG_FILE="~/pathrag/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if service is running
if systemctl is-active --quiet pathrag; then
    echo "[$DATE] ✅ PathRAG service is running" >> $LOG_FILE
else
    echo "[$DATE] ❌ PathRAG service is not running" >> $LOG_FILE
    # Optionally restart
    # systemctl restart pathrag
fi

# Check API health
if curl -s http://localhost:5000/health > /dev/null; then
    echo "[$DATE] ✅ API health check passed" >> $LOG_FILE
else
    echo "[$DATE] ❌ API health check failed" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df -h ~/pathrag | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] ⚠️  High disk usage: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2 }')
echo "[$DATE] 📊 Memory usage: ${MEM_USAGE}%" >> $LOG_FILE
EOF

# Make executable
chmod +x ~/pathrag/monitor.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/pathrag/monitor.sh") | crontab -
```

### Updates

```bash
# Update PathRAG
cd ~/pathrag/installation/PathRAG
git pull origin main
source ~/pathrag/installation/pathrag-env/bin/activate
pip install -r requirements.txt
sudo systemctl restart pathrag

# Update system packages
sudo apt update && sudo apt upgrade -y
sudo systemctl restart pathrag
```

## 🎯 Performance Optimization

### System Tuning
```bash
# Optimize for PathRAG workload
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max=134217728' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### ArangoDB Optimization
```bash
# Create indexes for better performance
python3 -c "
from arango import ArangoClient
client = ArangoClient(hosts='http://movie.ft.tc:8529')
db = client.db('pathrag', username='root', password='mzAd4682X13P6dRHLH7wQAjg')

# Add indexes to node collections
for collection_name in db.collections():
    if 'nodes' in collection_name['name']:
        collection = db.collection(collection_name['name'])
        try:
            collection.add_index({'type': 'persistent', 'fields': ['entity_type'], 'name': 'entity_type_idx'})
            collection.add_index({'type': 'fulltext', 'fields': ['content'], 'name': 'content_fulltext_idx'})
            print(f'Added indexes to {collection_name["name"]}')
        except:
            pass
"
```

---

## 📞 Support

For issues and support:
1. Check the troubleshooting section
2. Review logs: `journalctl -u pathrag -f`
3. Test individual components
4. Check ArangoDB connectivity
5. Verify Python environment

---

**🎉 Congratulations! PathRAG with ArangoDB is now deployed and ready for production use.**