# PathRAG Dual Environment Management Guide

This document provides exact step-by-step instructions for managing both Ubuntu production and Windows development environments for PathRAG.

## 📚 Related Documentation

- **[Quick Reference Commands](quick-reference-commands.md)** - Daily operation commands
- **[Troubleshooting Guide](troubleshooting-guide.md)** - Problem diagnosis and solutions
- **[Environment Sync Guide](../ENVIRONMENT_SYNC_GUIDE.md)** - Detailed synchronization workflows

## 📋 Environment Overview

### 🐧 Ubuntu Production Environment
- **Server**: Ubuntu production server
- **Branch**: `production`
- **API Server**: `src/api_server_simple.py`
- **Port**: 8000
- **Domain**: movie.ft.tc:8000
- **Database**: ArangoDB (movie.ft.tc:8529)
- **Process Manager**: PM2
- **Reverse Proxy**: Nginx
- **Purpose**: Stable production API

### 🖥️ Windows Development Environment
- **Platform**: Windows development machine
- **Branch**: `master`
- **API Server**: `src/api_server.py`
- **Port**: 5000 (default)
- **Database**: ArangoDB (localhost:8529)
- **Process Manager**: Manual/IDE
- **Purpose**: Full PathRAG development

## 🚀 Initial Setup

### Ubuntu Production Server Setup

1. **Clone Repository**
   ```bash
   cd /opt/pathrag
   git clone git@github.com:jomapps/pathrag.git
   cd pathrag
   git checkout production
   ```

2. **Setup Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install Flask Flask-CORS python-arango python-dotenv pydantic
   ```

3. **Configure Environment**
   ```bash
   cp example.env .env
   # Edit .env with production settings:
   # ARANGODB_HOST=movie.ft.tc
   # ARANGODB_PORT=8529
   # FLASK_PORT=8000
   ```

4. **Setup PM2**
   ```bash
   npm install -g pm2
   pm2 start ecosystem.config.js
   pm2 save
   pm2 startup
   ```

5. **Configure Nginx**
   ```bash
   sudo cp pathrag-nginx.conf /etc/nginx/sites-available/pathrag
   sudo ln -sf /etc/nginx/sites-available/pathrag /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Windows Development Setup

1. **Clone Repository**
   ```powershell
   git clone https://github.com/jomapps/pathrag.git
   cd pathrag
   git checkout master
   ```

2. **Setup Python Environment**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```powershell
   copy example.env .env
   # Edit .env with development settings:
   # ARANGODB_HOST=localhost
   # ARANGODB_PORT=8529
   # FLASK_PORT=5000
   ```

4. **Install PathRAG Library**
   ```powershell
   # Install PathRAG from source or pip
   pip install pathrag
   ```

## 🔄 Daily Operations

### Starting Services

#### Ubuntu Production
```bash
# Check PM2 status
pm2 status

# Start if not running
pm2 start pathrag-api

# Check logs
pm2 logs pathrag-api

# Verify API health
curl http://localhost:8000/health
curl http://movie.ft.tc:8000/health
```

#### Windows Development
```powershell
# Activate virtual environment
venv\Scripts\activate

# Start API server
python src\api_server.py

# Test in browser
# Visit http://localhost:5000/health
```

### Stopping Services

#### Ubuntu Production
```bash
# Stop PM2 process
pm2 stop pathrag-api

# Or restart
pm2 restart pathrag-api
```

#### Windows Development
```powershell
# Stop with Ctrl+C in terminal
# Or close IDE/terminal
```

## 🔧 Development Workflow

### 1. Making Changes on Windows Development

```powershell
# 1. Ensure you're on master branch
git checkout master
git status

# 2. Make your changes
# Edit files as needed

# 3. Test locally
python src\api_server.py
# Test at http://localhost:5000

# 4. Commit changes
git add .
git commit -m "Development: [describe changes]"

# 5. Push to master
git push origin master
```

### 2. Deploying to Ubuntu Production

```bash
# 1. Switch to production branch
cd /opt/pathrag/pathrag
git checkout production

# 2. Fetch latest changes
git fetch origin

# 3. Merge development changes
git merge origin/master

# 4. Handle conflicts if any
# If conflicts occur:
# - Edit conflicted files manually
# - git add <resolved-files>
# - git commit -m "Merge: Resolve conflicts"

# 5. Test changes
python verify_environments.py

# 6. If tests pass, restart services
pm2 restart pathrag-api

# 7. Verify production
curl http://movie.ft.tc:8000/health

# 8. Push production branch
git push origin production
```

### 3. Production Hotfixes

```bash
# 1. Make hotfix on production
cd /opt/pathrag/pathrag
git checkout production

# 2. Edit files as needed
nano src/api_server_simple.py

# 3. Test changes
python verify_environments.py

# 4. Commit hotfix
git add .
git commit -m "Hotfix: [describe fix]"

# 5. Restart services
pm2 restart pathrag-api

# 6. Push hotfix
git push origin production
```

```powershell
# 7. Merge hotfix to development (on Windows)
git checkout master
git fetch origin
git merge origin/production
git push origin master
```

## 🧪 Testing and Verification

### Automated Verification

Run on both environments:
```bash
python verify_environments.py
```

Expected output:
```
🔍 PathRAG Environment Verification
Environment: ubuntu_production / windows_development
============================================================
✅ Git Repository Status
✅ Python Environment
✅ API Server Health
✅ Database Connection
✅ Process Management
✅ Nginx Configuration (production only)
============================================================
📊 Test Summary: 100.0% success rate
🎉 All tests passed! Environment is healthy.
```

### Manual Testing

#### Ubuntu Production
```bash
# 1. Check PM2 status
pm2 status
pm2 logs pathrag-api --lines 50

# 2. Test API endpoints
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/
curl -X GET http://localhost:8000/docs

# 3. Test domain access
curl -X GET http://movie.ft.tc:8000/health

# 4. Test query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "mode": "local"}'

# 5. Check Nginx status
sudo systemctl status nginx
nginx -t

# 6. Check logs
sudo tail -f /var/log/nginx/pathrag_access.log
sudo tail -f /var/log/nginx/pathrag_error.log
```

#### Windows Development
```powershell
# 1. Start server
python src\api_server.py

# 2. Test in browser or PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET

# 3. Test query endpoint
$body = @{
    query = "test query"
    mode = "local"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -Body $body -ContentType "application/json"
```

### Live API Testing

Run comprehensive API tests:
```bash
# Ubuntu Production
python test_api_live.py

# Expected output:
# ✅ Health Check (localhost)
# ✅ Health Check (domain)
# ✅ Root API Information
# ✅ API Documentation
# ✅ Query Endpoint
# ✅ Insert Endpoint
# 🎉 ALL TESTS PASSED!
```

## 🚨 Troubleshooting

### Common Issues

#### Ubuntu Production Issues

**PM2 Process Not Running**
```bash
# Check PM2 status
pm2 status

# Start if stopped
pm2 start ecosystem.config.js

# Check logs for errors
pm2 logs pathrag-api

# Restart if needed
pm2 restart pathrag-api
```

**Nginx Issues**
```bash
# Test configuration
nginx -t

# Check if site is enabled
ls -la /etc/nginx/sites-enabled/pathrag

# Reload configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

**Database Connection Issues**
```bash
# Test ArangoDB connection
curl http://movie.ft.tc:8529/_api/version

# Check environment variables
cat .env | grep ARANGODB

# Test via API
curl http://localhost:8000/health
```

#### Windows Development Issues

**Python Environment Issues**
```powershell
# Check virtual environment
venv\Scripts\activate
python --version
pip list

# Reinstall dependencies
pip install -r requirements.txt
```

**PathRAG Import Issues**
```powershell
# Install PathRAG
pip install pathrag

# Or install from source
git clone https://github.com/microsoft/graphrag.git
cd graphrag
pip install -e .
```

**Port Conflicts**
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <process_id> /F

# Or use different port in .env
# FLASK_PORT=5001
```

### Emergency Procedures

#### Production Server Down
```bash
# 1. Check PM2 status
pm2 status

# 2. Check logs
pm2 logs pathrag-api --lines 100

# 3. Restart services
pm2 restart pathrag-api

# 4. If still failing, check Nginx
sudo systemctl status nginx
sudo systemctl restart nginx

# 5. Check database
curl http://movie.ft.tc:8529/_api/version

# 6. If all else fails, rollback
git log --oneline -5
git reset --hard HEAD~1
pm2 restart pathrag-api
```

#### Development Environment Broken
```powershell
# 1. Reset to last working commit
git status
git reset --hard origin/master

# 2. Clean Python environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Reset configuration
copy example.env .env
# Edit .env with correct settings
```

## 📊 Monitoring and Maintenance

### Daily Checks
```bash
# Ubuntu Production
pm2 status
curl http://movie.ft.tc:8000/health
python verify_environments.py
```

### Weekly Maintenance
```bash
# Update system packages (Ubuntu)
sudo apt update && sudo apt upgrade

# Check disk space
df -h

# Review logs
pm2 logs pathrag-api --lines 100
sudo tail -100 /var/log/nginx/pathrag_error.log

# Run full verification
python verify_environments.py
```

### Monthly Tasks
```bash
# Backup database
# (Add your ArangoDB backup commands here)

# Update dependencies (test in development first)
pip list --outdated

# Review and clean logs
pm2 flush
sudo logrotate -f /etc/logrotate.conf
```

## 📞 Support Checklist

When reporting issues, provide:

1. **Environment**: Ubuntu production or Windows development
2. **Branch**: Current git branch (`git branch --show-current`)
3. **Verification results**: Output of `python verify_environments.py`
4. **Error logs**: PM2 logs or console output
5. **Steps to reproduce**: Exact commands that caused the issue

Remember: **Always test changes in development before deploying to production!**
