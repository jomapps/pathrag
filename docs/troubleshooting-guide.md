# PathRAG Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Ubuntu Production Server Issues

#### Issue: PM2 Process Not Running
**Symptoms:**
- `pm2 status` shows process as "stopped" or "errored"
- API endpoints return connection refused

**Diagnosis:**
```bash
pm2 status
pm2 logs pathrag-api --lines 50
```

**Solutions:**
```bash
# 1. Restart the process
pm2 restart pathrag-api

# 2. If restart fails, delete and recreate
pm2 delete pathrag-api
pm2 start ecosystem.config.js

# 3. Check for port conflicts
sudo netstat -tulpn | grep :8000

# 4. Check virtual environment
source venv/bin/activate
python src/api_server_simple.py  # Test manually

# 5. Verify dependencies
pip list | grep -E "(flask|arango)"
```

#### Issue: Nginx Configuration Problems
**Symptoms:**
- `nginx -t` fails
- 502 Bad Gateway errors
- Domain not accessible

**Diagnosis:**
```bash
nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

**Solutions:**
```bash
# 1. Fix configuration syntax
sudo nano /etc/nginx/sites-available/pathrag
nginx -t

# 2. Ensure site is enabled
sudo ln -sf /etc/nginx/sites-available/pathrag /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# 3. Check upstream server
curl http://localhost:8000/health

# 4. Restart Nginx
sudo systemctl restart nginx

# 5. Check firewall
sudo ufw status
sudo ufw allow 80
sudo ufw allow 8000
```

#### Issue: Database Connection Failed
**Symptoms:**
- Health check shows "arangodb: disconnected"
- Query endpoints return database errors

**Diagnosis:**
```bash
curl http://movie.ft.tc:8529/_api/version
cat .env | grep ARANGODB
```

**Solutions:**
```bash
# 1. Test direct connection
curl -u root:password http://movie.ft.tc:8529/_api/version

# 2. Check environment variables
cat .env
# Verify ARANGODB_HOST, PORT, USERNAME, PASSWORD

# 3. Test from Python
python3 -c "
from arango import ArangoClient
client = ArangoClient(hosts='http://movie.ft.tc:8529')
db = client.db('pathrag', username='root', password='your_password')
print(db.version())
"

# 4. Restart ArangoDB (if you have access)
sudo systemctl restart arangodb3

# 5. Check network connectivity
ping movie.ft.tc
telnet movie.ft.tc 8529
```

#### Issue: Git Synchronization Problems
**Symptoms:**
- `git merge` conflicts
- Push/pull failures
- Verification script reports git issues

**Diagnosis:**
```bash
git status
git log --oneline --graph --all -10
git remote -v
```

**Solutions:**
```bash
# 1. Resolve merge conflicts
git status
# Edit conflicted files
git add <resolved_files>
git commit -m "Resolve merge conflicts"

# 2. Force sync with remote (CAREFUL!)
git fetch origin
git reset --hard origin/production

# 3. Fix divergent branches
git config pull.rebase false
git pull origin production

# 4. Clean working directory
git clean -fd
git reset --hard HEAD

# 5. Re-establish tracking
git branch --set-upstream-to=origin/production production
```

### Windows Development Issues

#### Issue: Python Environment Problems
**Symptoms:**
- Import errors
- Module not found errors
- Virtual environment not working

**Diagnosis:**
```powershell
python --version
pip list
Get-Command python
```

**Solutions:**
```powershell
# 1. Recreate virtual environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Install missing dependencies
pip install pathrag
pip install Flask Flask-CORS python-arango

# 3. Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# 4. Use specific Python version
py -3.9 -m venv venv
# or
python3 -m venv venv

# 5. Install from requirements
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Issue: Port Conflicts
**Symptoms:**
- "Address already in use" errors
- Cannot start development server

**Diagnosis:**
```powershell
netstat -ano | findstr :5000
Get-Process -Id <PID>
```

**Solutions:**
```powershell
# 1. Kill conflicting process
taskkill /PID <process_id> /F

# 2. Use different port
# Edit .env file:
# FLASK_PORT=5001

# 3. Find and kill Python processes
Get-Process python | Stop-Process -Force

# 4. Restart as administrator
# Run PowerShell as Administrator

# 5. Check Windows Defender/Firewall
# Add exception for Python/Flask
```

#### Issue: PathRAG Import Errors
**Symptoms:**
- "No module named 'pathrag'" errors
- Import failures in development

**Diagnosis:**
```powershell
python -c "import pathrag; print(pathrag.__version__)"
pip show pathrag
```

**Solutions:**
```powershell
# 1. Install PathRAG
pip install pathrag

# 2. Install from source
git clone https://github.com/microsoft/graphrag.git
cd graphrag
pip install -e .

# 3. Add to Python path
$env:PYTHONPATH = "C:\path\to\pathrag;$env:PYTHONPATH"

# 4. Install development version
pip install git+https://github.com/microsoft/graphrag.git

# 5. Check for conflicts
pip list | findstr pathrag
pip uninstall pathrag
pip install pathrag
```

### Cross-Platform Issues

#### Issue: Environment Synchronization Failures
**Symptoms:**
- Different behavior between environments
- Tests pass in one environment but fail in another

**Diagnosis:**
```bash
python verify_environments.py
git diff master..production
```

**Solutions:**
```bash
# 1. Ensure correct branches
# Windows: git checkout master
# Ubuntu: git checkout production

# 2. Sync environment files
# Copy .env settings appropriately
# Don't sync database credentials

# 3. Check dependency versions
pip freeze > requirements_current.txt
# Compare between environments

# 4. Verify API server versions
# Windows uses: src/api_server.py
# Ubuntu uses: src/api_server_simple.py

# 5. Run verification on both
python verify_environments.py
```

#### Issue: API Response Differences
**Symptoms:**
- Different API responses between environments
- Features work in dev but not production

**Diagnosis:**
```bash
# Compare API responses
curl http://localhost:5000/health  # Windows
curl http://movie.ft.tc:8000/health  # Ubuntu
```

**Solutions:**
```bash
# 1. Check API server versions
# Ensure you're using the right server for each environment

# 2. Verify environment variables
cat .env | grep -v PASSWORD

# 3. Check database content
# Ensure both databases have same data structure

# 4. Compare dependencies
pip list > deps_env1.txt
# Compare between environments

# 5. Test with same data
# Use identical test datasets
```

## 🔧 Diagnostic Commands

### System Health Check
```bash
# Ubuntu Production
python verify_environments.py
pm2 status
nginx -t
curl http://movie.ft.tc:8000/health
df -h
free -h

# Windows Development
python verify_environments.py
python -c "import pathrag; print('PathRAG OK')"
curl http://localhost:5000/health
```

### Log Analysis
```bash
# Ubuntu Production
pm2 logs pathrag-api --lines 100 | grep -i error
sudo tail -100 /var/log/nginx/pathrag_error.log
sudo journalctl -u nginx --since "1 hour ago"

# Windows Development
# Check console output for errors
# Check Windows Event Viewer if needed
```

### Network Connectivity
```bash
# Test database connection
curl http://movie.ft.tc:8529/_api/version

# Test API endpoints
curl -v http://movie.ft.tc:8000/health
curl -v http://localhost:8000/health

# Check DNS resolution
nslookup movie.ft.tc
ping movie.ft.tc
```

### Performance Analysis
```bash
# Check response times
time curl http://movie.ft.tc:8000/health

# Monitor resources
pm2 monit
htop

# Test load
ab -n 10 -c 2 http://movie.ft.tc:8000/health
```

## 🆘 Emergency Recovery Procedures

### Complete Production Failure
```bash
# 1. Stop all services
pm2 stop all
sudo systemctl stop nginx

# 2. Check system resources
df -h
free -h
ps aux | head -20

# 3. Restart services one by one
sudo systemctl start nginx
pm2 start pathrag-api

# 4. If still failing, rollback code
git log --oneline -5
git reset --hard HEAD~1
pm2 restart pathrag-api

# 5. Last resort: restore from backup
# (Implement your backup restoration procedure)
```

### Development Environment Corruption
```powershell
# 1. Reset git repository
git status
git reset --hard origin/master
git clean -fd

# 2. Recreate Python environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Reset configuration
copy example.env .env
# Edit .env with correct settings

# 4. Test basic functionality
python src\api_server.py
```

### Database Recovery
```bash
# 1. Test database connectivity
curl http://movie.ft.tc:8529/_api/version

# 2. Check database status
curl -u root:password http://movie.ft.tc:8529/_api/database

# 3. Recreate database if needed
# (Add your database recreation commands)

# 4. Restore from backup
# (Add your backup restoration commands)

# 5. Verify data integrity
curl http://localhost:8000/health
```

## 📞 When to Escalate

### Immediate Escalation Required
- Production API down > 5 minutes
- Database corruption or data loss
- Security breach indicators
- Multiple system failures

### Information to Collect Before Escalating
```bash
# 1. System status
python verify_environments.py > system_status.txt

# 2. Error logs
pm2 logs pathrag-api --lines 200 > error_logs.txt
sudo tail -200 /var/log/nginx/pathrag_error.log > nginx_errors.txt

# 3. System information
uname -a > system_info.txt
df -h > disk_usage.txt
free -h > memory_usage.txt
ps aux > running_processes.txt

# 4. Recent changes
git log --oneline -20 > recent_commits.txt
git diff HEAD~5 > recent_changes.txt

# 5. Configuration
cat .env | grep -v PASSWORD > config_sanitized.txt
```

### Self-Service Resolution Time Limits
- **Simple issues**: 15 minutes
- **Configuration problems**: 30 minutes
- **Complex debugging**: 1 hour
- **System failures**: Immediate escalation

Remember: **Document what you tried before escalating!**
