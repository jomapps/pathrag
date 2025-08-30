# PathRAG Documentation Index

Welcome to the PathRAG documentation. This index provides quick access to all documentation for managing your dual-environment PathRAG setup.

## 🏗️ Environment Architecture

PathRAG operates in two distinct environments:

### 🐧 Ubuntu Production Environment
- **Purpose**: Stable production API server
- **Branch**: `production`
- **API**: Simplified stable server (`api_server_simple.py`)
- **Domain**: movie.ft.tc:8000
- **Management**: PM2 + Nginx

### 🖥️ Windows Development Environment
- **Purpose**: Full PathRAG development and testing
- **Branch**: `master`
- **API**: Full PathRAG server (`api_server.py`)
- **Local**: localhost:5000
- **Management**: Manual/IDE

## 📖 Documentation Structure

### 🚀 Getting Started
1. **[Dual Environment Management Guide](dual-environment-management.md)**
   - Complete setup instructions for both environments
   - Step-by-step deployment procedures
   - Environment configuration details
   - **Start here for initial setup**

### 📋 Daily Operations
2. **[Quick Reference Commands](quick-reference-commands.md)**
   - Essential commands for daily operations
   - Service management (PM2, Nginx)
   - Git synchronization workflows
   - Testing and monitoring commands
   - **Use this for day-to-day tasks**

### 🔄 Synchronization
3. **[Environment Sync Guide](../ENVIRONMENT_SYNC_GUIDE.md)**
   - Detailed synchronization workflows
   - Development to production deployment
   - Production hotfix procedures
   - Conflict resolution strategies
   - **Reference for code deployment**

### 🚨 Problem Solving
4. **[Troubleshooting Guide](troubleshooting-guide.md)**
   - Common issues and solutions
   - Diagnostic procedures
   - Emergency recovery steps
   - When to escalate issues
   - **Use when things go wrong**

### 🧪 Testing and Verification
5. **Automated Tools**
   - `verify_environments.py` - Automated environment health checks
   - `test_api_live.py` - Live API endpoint testing
   - **Run these regularly to ensure health**

## 🎯 Quick Start Checklist

### For New Team Members

#### Ubuntu Production Access
```bash
# 1. Access the server
ssh user@production-server

# 2. Navigate to PathRAG
cd /opt/pathrag/pathrag

# 3. Check current status
python verify_environments.py
pm2 status
curl http://movie.ft.tc:8000/health
```

#### Windows Development Setup
```powershell
# 1. Clone repository
git clone https://github.com/jomapps/pathrag.git
cd pathrag
git checkout master

# 2. Setup environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure and test
copy example.env .env
# Edit .env with development settings
python src\api_server.py
```

## 🔧 Essential Commands

### Health Checks
```bash
# Verify both environments
python verify_environments.py

# Check production API
curl http://movie.ft.tc:8000/health

# Check development API
curl http://localhost:5000/health
```

### Service Management
```bash
# Ubuntu Production
pm2 status
pm2 restart pathrag-api
pm2 logs pathrag-api

# Windows Development
python src\api_server.py
```

### Git Synchronization
```bash
# Development to Production
git checkout master && git push origin master
git checkout production && git merge origin/master && git push origin production

# Production Hotfix to Development
git checkout production && git push origin production
git checkout master && git merge origin/production && git push origin master
```

## 📊 Monitoring and Maintenance

### Daily Checks
- [ ] Run `python verify_environments.py`
- [ ] Check `pm2 status` on production
- [ ] Verify API health endpoints
- [ ] Review error logs

### Weekly Tasks
- [ ] Update system packages
- [ ] Review and clean logs
- [ ] Check disk space and resources
- [ ] Test backup procedures

### Monthly Tasks
- [ ] Update dependencies (test in dev first)
- [ ] Review security updates
- [ ] Backup database
- [ ] Performance analysis

## 🚨 Emergency Procedures

### Production Down
1. Check PM2 status: `pm2 status`
2. Check logs: `pm2 logs pathrag-api`
3. Restart services: `pm2 restart pathrag-api`
4. Check Nginx: `nginx -t && sudo systemctl status nginx`
5. If needed, rollback: `git reset --hard HEAD~1`

### Development Issues
1. Reset environment: `git reset --hard origin/master`
2. Recreate venv: `Remove-Item venv; python -m venv venv`
3. Reinstall deps: `pip install -r requirements.txt`
4. Test: `python src\api_server.py`

## 📞 Support and Escalation

### Self-Service Time Limits
- **Simple issues**: 15 minutes
- **Configuration problems**: 30 minutes
- **Complex debugging**: 1 hour
- **System failures**: Immediate escalation

### Before Escalating, Collect:
```bash
# System status
python verify_environments.py > system_status.txt

# Recent logs
pm2 logs pathrag-api --lines 100 > recent_logs.txt

# Git history
git log --oneline -10 > recent_commits.txt

# System resources
df -h > disk_usage.txt && free -h > memory_usage.txt
```

## 🔗 External Resources

### PathRAG Project
- [PathRAG GitHub Repository](https://github.com/microsoft/graphrag)
- [PathRAG Documentation](https://microsoft.github.io/graphrag/)

### Dependencies
- [ArangoDB Documentation](https://www.arangodb.com/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### System Administration
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Git Documentation](https://git-scm.com/doc)

## 📝 Documentation Maintenance

### Updating Documentation
1. Make changes in development environment first
2. Test all commands and procedures
3. Update version numbers and dates
4. Sync to production branch
5. Notify team of changes

### Contributing
- Follow existing format and style
- Include exact commands and expected outputs
- Test all procedures before documenting
- Add troubleshooting sections for new features

## 🏷️ Version Information

- **Documentation Version**: 1.0
- **Last Updated**: 2025-08-30
- **PathRAG Version**: Compatible with current production deployment
- **Environments**: Ubuntu 22.04+ (Production), Windows 10+ (Development)

---

**Remember**: Always test changes in development before deploying to production!

For immediate help, start with the [Quick Reference Commands](quick-reference-commands.md) or [Troubleshooting Guide](troubleshooting-guide.md).
