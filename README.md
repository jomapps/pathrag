# PathRAG with ArangoDB - One-Click Deployment Solution

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ArangoDB](https://img.shields.io/badge/ArangoDB-3.9+-orange.svg)](https://www.arangodb.com/)

A production-ready, one-click deployment solution for PathRAG (Path-based Retrieval-Augmented Generation) with ArangoDB as the graph database backend. This implementation provides a complete, scalable knowledge graph solution with REST API, containerized deployment, and comprehensive configuration management.

## 🚀 Features

- **One-Click Deployment**: Automated setup scripts for Windows, Linux, and Docker
- **ArangoDB Integration**: High-performance graph database backend
- **REST API**: Complete Flask-based API server with CORS support
- **Production Ready**: Nginx reverse proxy, logging, monitoring, and health checks
- **Containerized**: Docker and Docker Compose support
- **Configurable**: Environment-based configuration management
- **Scalable**: Designed for production workloads

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10+, Ubuntu 18.04+, or macOS 10.15+
- **Python**: 3.8 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space minimum
- **Network**: Internet connection for dependency installation

### Required Services
- **ArangoDB**: 3.9 or higher
- **OpenAI API**: Valid API key for embeddings and LLM

## 🛠️ Quick Start

### Option 1: Windows Development Setup

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/pathrag/pathrag-arangodb.git
   cd pathrag-arangodb
   ```

2. **Run the Windows deployment script**:
   ```powershell
   .\deploy\deploy-windows.ps1
   ```

3. **Configure environment**:
   ```powershell
   cp example.env .env
   # Edit .env with your settings
   ```

4. **Start the service**:
   ```powershell
   python src\api_server.py
   ```

### Option 2: Linux/Unix Production Setup

1. **Clone and deploy**:
   ```bash
   git clone https://github.com/pathrag/pathrag-arangodb.git
   cd pathrag-arangodb
   sudo ./deploy/deploy.sh
   ```

2. **Configure environment**:
   ```bash
   sudo cp example.env /etc/pathrag/.env
   sudo nano /etc/pathrag/.env
   ```

3. **Start services**:
   ```bash
   sudo systemctl start pathrag
   sudo systemctl start nginx
   ```

### Option 3: Docker Deployment

1. **Clone and start**:
   ```bash
   git clone https://github.com/pathrag/pathrag-arangodb.git
   cd pathrag-arangodb
   cp example.env .env
   # Edit .env with your settings
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Copy `example.env` to `.env` and configure the following key settings:

```env
# ArangoDB Configuration
ARANGODB_HOST=localhost
ARANGODB_PORT=8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=your_password
ARANGODB_DATABASE=pathrag

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# PathRAG Configuration
PATHRAG_WORKING_DIR=./pathrag_data
PATHRAG_CHUNK_TOKEN_SIZE=1200
PATHRAG_EMBEDDING_BATCH_NUM=32

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=false
```

### Advanced Configuration

For detailed configuration options, see the [Configuration Guide](docs/pathrag-arangodb-implementation-guide.md).

## 📚 API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

### Insert Documents
```bash
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Your document content here...",
      "Another document..."
    ]
  }'
```

### Query Knowledge Base
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "params": {
      "mode": "hybrid",
      "top_k": 10
    }
  }'
```

### Insert Custom Knowledge Graph
```bash
curl -X POST http://localhost:5000/insert_custom_kg \
  -H "Content-Type: application/json" \
  -d '{
    "custom_kg": {
      "chunks": [...],
      "entities": [...],
      "relationships": [...]
    }
  }'
```

### Delete Entity
```bash
curl -X DELETE http://localhost:5000/delete_entity \
  -H "Content-Type: application/json" \
  -d '{"entity_name": "EntityName"}'
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  Flask API      │────│   PathRAG Core  │
│   (Port 80)     │    │   (Port 5000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ArangoDB      │    │   OpenAI API    │
                       │   (Port 8529)   │    │   (External)    │
                       └─────────────────┘    └─────────────────┘
```

### Components

- **PathRAG Core**: Knowledge graph processing and retrieval engine
- **ArangoDB Storage**: Graph database for entities, relationships, and vectors
- **Flask API**: REST API server with comprehensive endpoints
- **Nginx**: Reverse proxy with load balancing and SSL termination
- **Configuration Management**: Environment-based settings with validation

## 🧪 Testing

### Run Health Checks
```bash
# Test ArangoDB connection
curl http://localhost:5000/health

# Get system status
curl http://localhost:5000/status

# Get configuration info
curl http://localhost:5000/config
```

### Run Integration Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 📁 Project Structure

```
pathrag-arangodb/
├── src/
│   ├── PathRAG/              # Original PathRAG repository
│   ├── arangodb_storage.py   # ArangoDB storage implementation
│   └── api_server.py         # Flask API server
├── config/
│   ├── config.py             # Configuration management
│   ├── pathrag_factory.py    # PathRAG instance factory
│   └── __init__.py
├── deploy/
│   ├── deploy.sh             # Linux deployment script
│   ├── deploy-windows.ps1    # Windows deployment script
│   ├── docker-compose.yml    # Docker Compose configuration
│   ├── Dockerfile            # Container definition
│   └── nginx.conf            # Nginx configuration
├── docs/                     # Documentation
├── tests/                    # Test files
├── examples/                 # Usage examples
├── scripts/                  # Utility scripts
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── example.env               # Environment template
└── README.md                 # This file
```

## 🔧 Troubleshooting

### Common Issues

1. **ArangoDB Connection Failed**
   ```bash
   # Check ArangoDB status
   sudo systemctl status arangodb3
   
   # Restart ArangoDB
   sudo systemctl restart arangodb3
   ```

2. **OpenAI API Errors**
   - Verify your API key in `.env`
   - Check API quota and billing
   - Ensure network connectivity

3. **Memory Issues**
   - Increase system memory
   - Reduce `PATHRAG_EMBEDDING_BATCH_NUM`
   - Adjust `PATHRAG_CHUNK_TOKEN_SIZE`

4. **Port Conflicts**
   - Change `API_PORT` in `.env`
   - Update Nginx configuration
   - Check for running services

### Logs

```bash
# Application logs
tail -f logs/pathrag_api.log

# System logs (Linux)
sudo journalctl -u pathrag -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# ArangoDB logs
sudo tail -f /var/log/arangodb3/arangodb3.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PathRAG](https://github.com/JoshuaC215/PathRAG) - Original PathRAG implementation
- [ArangoDB](https://www.arangodb.com/) - Multi-model database
- [OpenAI](https://openai.com/) - Language models and embeddings

## 📞 Support

- **Documentation**: [Implementation Guide](docs/pathrag-arangodb-implementation-guide.md)
- **Issues**: [GitHub Issues](https://github.com/pathrag/pathrag-arangodb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pathrag/pathrag-arangodb/discussions)

---

**Made with ❤️ for the AI and Knowledge Graph community**