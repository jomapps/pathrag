# PathRAG Quick Reference Commands

## 🚀 Daily Operations

### Ubuntu Production Server

#### Service Management
```bash
# Check status
pm2 status
pm2 logs pathrag-api

# Start/Stop/Restart
pm2 start pathrag-api
pm2 stop pathrag-api
pm2 restart pathrag-api

# Health check
curl http://localhost:8000/health
curl http://movie.ft.tc:8000/health
```

#### Git Operations
```bash
# Check status
git status
git branch --show-current

# Sync with development
git fetch origin
git merge origin/master
git push origin production

# Emergency rollback
git reset --hard HEAD~1
pm2 restart pathrag-api
```

#### System Checks
```bash
# Nginx
nginx -t
sudo systemctl status nginx
sudo systemctl reload nginx

# Logs
pm2 logs pathrag-api --lines 50
sudo tail -f /var/log/nginx/pathrag_error.log

# Verification
python verify_environments.py
```

### Windows Development

#### Service Management
```powershell
# Start development server
venv\Scripts\activate
python src\api_server.py

# Test
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
```

#### Git Operations
```powershell
# Development workflow
git checkout master
git add .
git commit -m "Development: [changes]"
git push origin master

# Sync with production
git fetch origin
git merge origin/production
```

## 🔄 Synchronization Workflows

### Development → Production
```bash
# On Windows (Development)
git checkout master
git add .
git commit -m "Development: [changes]"
git push origin master

# On Ubuntu (Production)
git checkout production
git fetch origin
git merge origin/master
python verify_environments.py
pm2 restart pathrag-api
curl http://movie.ft.tc:8000/health
git push origin production
```

### Production Hotfix → Development
```bash
# On Ubuntu (Production)
git checkout production
# Make changes
git add .
git commit -m "Hotfix: [fix]"
pm2 restart pathrag-api
git push origin production

# On Windows (Development)
git checkout master
git fetch origin
git merge origin/production
git push origin master
```

## 🧪 Testing Commands

### Automated Testing
```bash
# Full environment verification
python verify_environments.py

# Live API testing
python test_api_live.py
```

### Manual API Testing

#### Health Check
```bash
# Ubuntu Production
curl http://localhost:8000/health
curl http://movie.ft.tc:8000/health

# Windows Development
curl http://localhost:5000/health
```

#### Query Testing
```bash
# Ubuntu Production
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "local"}'

# Windows Development
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "local"}'
```

#### Insert Testing
```bash
# Ubuntu Production
curl -X POST http://localhost:8000/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "test document", "metadata": {}}'

# Windows Development
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "test document", "metadata": {}}'
```

## 🚨 Emergency Commands

### Production Server Issues

#### PM2 Problems
```bash
# Kill all PM2 processes
pm2 kill

# Restart PM2
pm2 start ecosystem.config.js
pm2 save
```

#### Nginx Problems
```bash
# Test configuration
nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### Database Issues
```bash
# Test ArangoDB
curl http://movie.ft.tc:8529/_api/version

# Check connection via API
curl http://localhost:8000/health | jq '.services.arangodb'
```

#### Git Issues
```bash
# Reset to last working state
git status
git reset --hard HEAD~1

# Force sync with remote
git fetch origin
git reset --hard origin/production
```

### Development Environment Issues

#### Python Environment
```powershell
# Reset virtual environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Port Conflicts
```powershell
# Find process using port
netstat -ano | findstr :5000

# Kill process
taskkill /PID <process_id> /F
```

#### Git Reset
```powershell
# Reset to master
git checkout master
git reset --hard origin/master
```

## 📊 Monitoring Commands

### System Health
```bash
# Ubuntu Production
# Disk space
df -h

# Memory usage
free -h

# CPU usage
top -n 1

# Process status
pm2 monit
```

### Log Monitoring
```bash
# Ubuntu Production
# PM2 logs
pm2 logs pathrag-api --lines 100

# Nginx logs
sudo tail -f /var/log/nginx/pathrag_access.log
sudo tail -f /var/log/nginx/pathrag_error.log

# System logs
sudo journalctl -u nginx -f
```

### Performance Testing
```bash
# Load testing (install apache2-utils first)
ab -n 100 -c 10 http://movie.ft.tc:8000/health

# Response time testing
time curl http://movie.ft.tc:8000/health
```

## 🔧 Configuration Commands

### Environment Variables
```bash
# View current settings
cat .env | grep -v PASSWORD

# Edit environment
nano .env

# Reload PM2 with new environment
pm2 restart pathrag-api
```

### Nginx Configuration
```bash
# Test configuration
nginx -t

# Edit configuration
sudo nano /etc/nginx/sites-available/pathrag

# Reload configuration
sudo systemctl reload nginx
```

### PM2 Configuration
```bash
# View current configuration
cat ecosystem.config.js

# Edit configuration
nano ecosystem.config.js

# Apply new configuration
pm2 delete pathrag-api
pm2 start ecosystem.config.js
pm2 save
```

## 📋 Maintenance Checklists

### Daily Checklist
```bash
# 1. Check service status
pm2 status

# 2. Verify API health
curl http://movie.ft.tc:8000/health

# 3. Check for errors
pm2 logs pathrag-api --lines 20

# 4. Verify git status
git status
```

### Weekly Checklist
```bash
# 1. Run full verification
python verify_environments.py

# 2. Check system resources
df -h && free -h

# 3. Review logs
pm2 logs pathrag-api --lines 100

# 4. Update system (if needed)
sudo apt update && sudo apt list --upgradable
```

### Monthly Checklist
```bash
# 1. Backup database
# (Add your backup commands)

# 2. Clean logs
pm2 flush

# 3. Check for dependency updates
pip list --outdated

# 4. Review security
sudo apt list --upgradable | grep -i security
```

## 🆘 Emergency Contacts

### When to Escalate
- API down for > 5 minutes
- Database connection lost
- Multiple service failures
- Security incidents

### Information to Gather
```bash
# System status
python verify_environments.py > system_status.txt

# Recent logs
pm2 logs pathrag-api --lines 100 > recent_logs.txt

# Git status
git log --oneline -10 > recent_commits.txt

# System info
df -h > disk_usage.txt
free -h > memory_usage.txt
```

Remember: **When in doubt, check the logs first!**
