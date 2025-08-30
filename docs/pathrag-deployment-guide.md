# PathRAG Production Deployment Guide

## Overview

This guide provides a complete automated deployment solution for PathRAG with ArangoDB integration on Ubuntu production servers.

## Files Included

1. **pathrag-deploy.sh** - Complete automated deployment script (1007 lines)
2. **pathrag-deploy-server.sh** - Basic server setup script
3. **pathrag-arangodb-production-deployment.md** - Detailed manual deployment guide

## Quick Deployment

### Prerequisites
- Ubuntu 20.04+ LTS server
- Root access
- Internet connectivity
- ArangoDB server accessible at movie.ft.tc:8529

### Automated Deployment Steps

1. **Upload the deployment script to your server:**
   ```bash
   scp pathrag-deploy.sh root@YOUR_SERVER_IP:/root/
   ```

2. **SSH into your server:**
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

3. **Make the script executable and run:**
   ```bash
   chmod +x pathrag-deploy.sh
   ./pathrag-deploy.sh
   ```

## Configuration

The deployment script includes these pre-configured settings:

### ArangoDB Configuration
- **Host:** movie.ft.tc
- **Port:** 8529
- **Username:** root
- **Password:** mzAd4682X13P6dRHLH7wQAjg
- **Database:** pathrag

### PathRAG Configuration
- **User:** pathrag
- **Home Directory:** /home/pathrag/pathrag
- **Service Port:** 5000
- **Repository:** https://github.com/BUPT-GAMMA/PathRAG.git

### OpenAI Configuration
- **API Key:** your-openai-api-key-here

## What the Script Does

### System Setup
1. Updates Ubuntu packages
2. Installs Python 3.10, development tools, and dependencies
3. Creates dedicated `pathrag` user
4. Sets up directory structure

### PathRAG Installation
1. Creates Python virtual environment
2. Clones PathRAG repository
3. Installs all required Python packages
4. Creates ArangoDB storage implementation
5. Sets up configuration files

### Service Configuration
1. Creates Flask API server
2. Sets up systemd service
3. Configures firewall rules
4. Creates maintenance scripts

### Testing & Verification
1. Tests ArangoDB connectivity
2. Verifies PathRAG API endpoints
3. Runs deployment validation

## Post-Deployment

### Service Management
```bash
# Start PathRAG service
sudo systemctl start pathrag

# Enable auto-start on boot
sudo systemctl enable pathrag

# Check service status
sudo systemctl status pathrag

# View logs
journalctl -u pathrag -f
```

### API Endpoints
- **Health Check:** http://YOUR_SERVER_IP:5000/health
- **Status:** http://YOUR_SERVER_IP:5000/status
- **Insert Document:** POST http://YOUR_SERVER_IP:5000/insert
- **Query:** POST http://YOUR_SERVER_IP:5000/query

### Testing the Deployment
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test status endpoint
curl http://localhost:5000/status

# Insert a test document
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document for PathRAG.", "metadata": {"source": "test"}}'

# Query the system
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PathRAG?", "top_k": 5}'
```

## Directory Structure

After deployment, the following structure is created:

```
/home/pathrag/pathrag/
├── installation/
│   ├── pathrag-env/          # Python virtual environment
│   └── PathRAG/              # PathRAG source code
├── data/                     # Data storage
├── logs/                     # Application logs
├── config/                   # Configuration files
│   ├── pathrag.env          # Environment variables
│   ├── pathrag_config.py    # PathRAG configuration
│   └── arangodb_storage.py  # ArangoDB storage implementation
└── backups/                  # Backup storage
```

## Troubleshooting

### Common Issues

1. **ArangoDB Connection Failed**
   - Verify ArangoDB server is running at movie.ft.tc:8529
   - Check network connectivity
   - Verify credentials

2. **Service Won't Start**
   ```bash
   # Check service logs
   journalctl -u pathrag -n 50
   
   # Check Python environment
   sudo -u pathrag bash -c "cd /home/pathrag/pathrag/installation && source pathrag-env/bin/activate && python -c 'import pathrag'"
   ```

3. **Port Already in Use**
   ```bash
   # Check what's using port 5000
   sudo netstat -tulpn | grep :5000
   
   # Kill the process if needed
   sudo kill -9 <PID>
   ```

### Log Locations
- **Service Logs:** `journalctl -u pathrag`
- **Application Logs:** `/home/pathrag/pathrag/logs/pathrag.log`
- **System Logs:** `/var/log/syslog`

## Maintenance

### Backup
```bash
# Run backup script
/home/pathrag/pathrag/backup.sh
```

### Monitoring
```bash
# Run monitoring script
/home/pathrag/pathrag/monitor.sh
```

### Updates
```bash
# Update PathRAG
sudo -u pathrag bash -c "cd /home/pathrag/pathrag/installation/PathRAG && git pull origin main"

# Restart service
sudo systemctl restart pathrag
```

## Security Notes

- The script includes sensitive credentials (API keys, passwords)
- Change default passwords before production use
- Configure firewall rules appropriately
- Use HTTPS in production environments
- Regularly update system packages

## Support

For issues or questions:
1. Check the logs first
2. Verify all prerequisites are met
3. Ensure network connectivity to ArangoDB
4. Review the detailed deployment guide in `pathrag-arangodb-production-deployment.md`

---

**Last Updated:** August 27, 2024
**Script Version:** 1.0
**Compatible with:** Ubuntu 20.04+ LTS